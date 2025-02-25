# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-DB管理系统(BlueKing-BK-DBM) available.
Copyright (C) 2017-2023 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at https://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import copy
import logging.config
from collections import defaultdict
from dataclasses import asdict
from typing import Dict, Optional

from django.utils.translation import ugettext as _

from backend.components import DBConfigApi
from backend.components.dbconfig.constants import ConfType, FormatType, LevelName
from backend.configuration.constants import AffinityEnum, DBType
from backend.db_meta.api import common
from backend.db_meta.api.cluster.apis import query_cluster_by_hosts
from backend.db_meta.enums import InstanceInnerRole, InstanceRole
from backend.db_meta.enums.cluster_type import ClusterType
from backend.db_meta.enums.machine_type import MachineType
from backend.db_meta.models import Spec, StorageInstance
from backend.db_services.redis.util import is_redis_cluster_protocal
from backend.db_services.version.constants import RedisVersion
from backend.flow.consts import DEPENDENCIES_PLUGINS, ClusterStatus, InstanceStatus
from backend.flow.engine.bamboo.scene.common.builder import Builder, SubBuilder
from backend.flow.engine.bamboo.scene.common.get_file_list import GetFileList
from backend.flow.engine.bamboo.scene.redis.atom_jobs.reupload_old_backup_records import (
    RedisReuploadOldBackupRecordsAtomJob,
)
from backend.flow.plugins.components.collections.common.download_backup_client import DownloadBackupClientComponent
from backend.flow.plugins.components.collections.common.install_nodeman_plugin import (
    InstallNodemanPluginServiceComponent,
)
from backend.flow.plugins.components.collections.redis.exec_actuator_script import ExecuteDBActuatorScriptComponent
from backend.flow.plugins.components.collections.redis.get_redis_payload import GetRedisActPayloadComponent
from backend.flow.plugins.components.collections.redis.redis_config import RedisConfigComponent
from backend.flow.plugins.components.collections.redis.redis_db_meta import RedisDBMetaComponent
from backend.flow.plugins.components.collections.redis.trans_flies import TransFileComponent
from backend.flow.utils.common_act_dataclass import DownloadBackupClientKwargs, InstallNodemanPluginKwargs
from backend.flow.utils.redis.redis_act_playload import RedisActPayload
from backend.flow.utils.redis.redis_context_dataclass import ActKwargs, CommonContext
from backend.flow.utils.redis.redis_db_meta import RedisDBMeta

logger = logging.getLogger("flow")


class RedisClusterMigrateLoadFlow(object):
    """
    redis cache/ssd集群 迁移元数据
    """

    def __init__(self, root_id: str, data: Optional[Dict]):
        """
        @param root_id : 任务流程定义的root_id
        @param data : 单据传递过来的参数列表，是dict格式
        """
        self.root_id = root_id
        self.data = data

    def __dispose_cluster_params(self, cluster_info: dict) -> dict:
        """
        处理集群参数
        返回需要的处理后的数据格式
        """
        master_ips = []
        slave_ips = []
        spec_id_dict = {}
        seg_dict = {}
        role_dict = {}
        ip_port_dict = defaultdict(list)
        server_shards = defaultdict(dict)
        repl_list = []
        proxy_ips = [proxy["ip"] for proxy in cluster_info["proxies"]]
        proxy_spec_id = cluster_info["proxies"][0]["spec_id"]

        proxy_port = cluster_info["proxies"][0]["port"]
        for backend in cluster_info["backends"]:
            mip = backend["nodes"]["master"]["ip"]
            sip = backend["nodes"]["slave"]["ip"]
            mport = backend["nodes"]["master"]["port"]
            sport = backend["nodes"]["slave"]["port"]
            master_ips.append(mip)
            slave_ips.append(sip)
            ip_port_dict[mip].append(mport)
            ip_port_dict[sip].append(sport)
            spec_id_dict[mip] = backend["nodes"]["master"]["spec_id"]
            spec_id_dict[sip] = backend["nodes"]["slave"]["spec_id"]
            role_dict[mip] = "new_master_ips"
            role_dict[sip] = "new_slave_ips"
            seg_dict["{}:{}".format(mip, mport)] = backend["shard"]
            server_shards[mip]["{}:{}".format(mip, mport)] = backend["shard"]
            server_shards[sip]["{}:{}".format(sip, mport)] = backend["shard"]
            repl_list.append({"master_ip": mip, "master_port": int(mport), "slave_ip": sip, "slave_port": int(sport)})

        return {
            "spec_id_dict": spec_id_dict,
            "seg_dict": seg_dict,
            "repl_list": repl_list,
            "role_dict": role_dict,
            "ip_port_dict": dict(ip_port_dict),
            "proxy_ips": proxy_ips,
            "proxy_port": proxy_port,
            "proxy_spec_id": proxy_spec_id,
            "proxy_spec_config": Spec.objects.get(spec_id=proxy_spec_id).get_spec_info(),
            "master_ips": list(set(master_ips)),
            "slave_ips": list(set(slave_ips)),
            "server_shards": dict(server_shards),
        }

    # 检查传参的配置与配置中心当前版本模板是否匹配，是否多了配置
    def __check_config(self, bk_biz_id: str, conf_file: str, conf_type, namespace: str, conf: dict) -> dict:
        config_data = DBConfigApi.query_conf_item(
            params={
                "bk_biz_id": bk_biz_id,
                "level_name": LevelName.APP,
                "level_value": bk_biz_id,
                "conf_file": conf_file,
                "conf_type": conf_type,
                "namespace": namespace,
                "format": FormatType.MAP,
            }
        )
        # 传入的参数不在对应版本的配置中，需要删除
        redis_config_tpl = config_data["content"].keys()
        conf_copy = copy.deepcopy(conf)
        for k in conf_copy.keys():
            if k not in redis_config_tpl:
                del conf[k]
        return conf

    def __get_update_status_acts(self, sub_kwargs: ActKwargs, cluster: dict) -> list:
        acts_list = []
        act_kwargs = copy.deepcopy(sub_kwargs)
        for redis_ip in cluster["master_ips"] + cluster["slave_ips"]:
            act_kwargs.cluster["meta_update_ip"] = redis_ip
            act_kwargs.cluster["meta_update_ports"] = cluster["ip_port_dict"][redis_ip]
            act_kwargs.cluster["meta_update_status"] = InstanceStatus.RUNNING
            act_kwargs.cluster["meta_func_name"] = RedisDBMeta.instances_status_update.__name__
            acts_list.append(
                {
                    "act_name": _("{}-更新redis状态".format(redis_ip)),
                    "act_component_code": RedisDBMetaComponent.code,
                    "kwargs": asdict(act_kwargs),
                },
            )
        for proxy_ip in cluster["proxy_ips"]:
            act_kwargs.cluster["meta_update_ip"] = proxy_ip
            act_kwargs.cluster["meta_update_ports"] = [cluster["proxy_port"]]
            act_kwargs.cluster["meta_update_status"] = InstanceStatus.RUNNING
            act_kwargs.cluster["meta_func_name"] = RedisDBMeta.instances_status_update.__name__
            acts_list.append(
                {
                    "act_name": _("{}-更新proxy状态".format(proxy_ip)),
                    "act_component_code": RedisDBMetaComponent.code,
                    "kwargs": asdict(act_kwargs),
                },
            )
        return acts_list

    def redis_cluster_migrate_load_flow(self):
        """
        cache/ssd和rediscluster迁移流程，传参结构体是一样的，可以放一起处理
        """
        ins_status = InstanceStatus.UNAVAILABLE
        if self.data["migrate_ctl"]["dbha"]:
            ins_status = InstanceStatus.RUNNING
        proxy_type = MachineType.TWEMPROXY.value
        if self.data["db_type"] == ClusterType.TendisPredixyRedisCluster.value:
            proxy_type = MachineType.PREDIXY.value
        redis_pipeline = Builder(root_id=self.root_id, data=self.data)
        act_kwargs = ActKwargs()
        act_kwargs.set_trans_data_dataclass = CommonContext.__name__
        act_kwargs.is_update_trans_data = True
        cluster_tpl = {
            "created_by": self.data["created_by"],
            "bk_biz_id": self.data["bk_biz_id"],
            "bk_cloud_id": self.data["bk_cloud_id"],
        }

        sub_pipelines = []
        for params in self.data["clusters"]:
            cluster = self.__dispose_cluster_params(params)
            sub_pipeline = SubBuilder(root_id=self.root_id, data=self.data)
            act_kwargs.cluster = {
                "cluster_type": params["clusterinfo"]["cluster_type"],
                "db_version": params["clusterinfo"]["db_version"],
            }

            if ins_status == InstanceStatus.RUNNING and not self.data["migrate_ctl"]["meta"]:
                sub_pipeline.add_parallel_acts(self.__get_update_status_acts(act_kwargs, cluster))
                sub_pipelines.append(
                    sub_pipeline.build_sub_process(
                        sub_name=_("{}更新状态子任务").format(params["clusterinfo"]["immute_domain"])
                    )
                )
                continue

            if not self.data["migrate_ctl"]["meta"]:
                continue

            sub_pipeline.add_act(
                act_name=_("初始化配置"), act_component_code=GetRedisActPayloadComponent.code, kwargs=asdict(act_kwargs)
            )

            # 下发介质包
            all_ips = cluster["proxy_ips"] + cluster["master_ips"] + cluster["slave_ips"]
            trans_files = GetFileList(db_type=DBType.Redis)
            act_kwargs.file_list = trans_files.redis_dbmon()
            act_kwargs.exec_ip = all_ips
            sub_pipeline.add_act(
                act_name=_("下发介质包"),
                act_component_code=TransFileComponent.code,
                kwargs=asdict(act_kwargs),
            )

            # 安装插件
            acts_list = []
            acts_list.append(
                {
                    "act_name": _("安装backup-client工具").format(all_ips),
                    "act_component_code": DownloadBackupClientComponent.code,
                    "kwargs": asdict(
                        DownloadBackupClientKwargs(
                            bk_cloud_id=self.data["bk_cloud_id"],
                            bk_biz_id=int(self.data["bk_biz_id"]),
                            download_host_list=all_ips,
                        ),
                    ),
                }
            )
            for plugin_name in DEPENDENCIES_PLUGINS:
                acts_list.append(
                    {
                        "act_name": _("安装[{}]插件".format(plugin_name)),
                        "act_component_code": InstallNodemanPluginServiceComponent.code,
                        "kwargs": asdict(
                            InstallNodemanPluginKwargs(
                                bk_cloud_id=int(self.data["bk_cloud_id"]),
                                ips=cluster["master_ips"] + cluster["slave_ips"] + cluster["proxy_ips"],
                                plugin_name=plugin_name,
                            )
                        ),
                    }
                )
            sub_pipeline.add_parallel_acts(acts_list=acts_list)
            # 安装插件 end

            # ./dbactuator_redis --atom-job-list="sys_init"
            act_kwargs.get_redis_payload_func = RedisActPayload.get_sys_init_payload.__name__
            sub_pipeline.add_act(
                act_name=_("初始化机器"),
                act_component_code=ExecuteDBActuatorScriptComponent.code,
                kwargs=asdict(act_kwargs),
            )

            # proxy 相关操作
            act_kwargs.cluster = copy.deepcopy(cluster_tpl)
            act_kwargs.cluster["machine_type"] = proxy_type
            act_kwargs.cluster["cluster_type"] = params["clusterinfo"]["cluster_type"]
            # proxy元数据 - 批量写入
            act_kwargs.cluster["ins_status"] = ins_status
            act_kwargs.cluster["new_proxy_ips"] = cluster["proxy_ips"]
            act_kwargs.cluster["port"] = cluster["proxy_port"]
            act_kwargs.cluster["spec_id"] = cluster["proxy_spec_id"]
            act_kwargs.cluster["spec_config"] = cluster["proxy_spec_config"]
            act_kwargs.cluster["meta_func_name"] = RedisDBMeta.proxy_install.__name__
            sub_pipeline.add_act(
                act_name=_("Proxy写入元数据"),
                act_component_code=RedisDBMetaComponent.code,
                kwargs=asdict(act_kwargs),
            )

            # redis 相关操作
            # 写入元数据,后面实例的规格可能不一样，所以不能批量写入
            acts_list = []
            for redis_ip in cluster["master_ips"] + cluster["slave_ips"]:
                act_kwargs.cluster = copy.deepcopy(cluster_tpl)
                act_kwargs.cluster["cluster_type"] = params["clusterinfo"]["cluster_type"]
                act_kwargs.cluster["ins_status"] = ins_status

                act_kwargs.cluster[cluster["role_dict"][redis_ip]] = [redis_ip]
                act_kwargs.cluster["ports"] = cluster["ip_port_dict"][redis_ip]
                act_kwargs.cluster["spec_id"] = cluster["spec_id_dict"][redis_ip]
                act_kwargs.cluster["spec_config"] = Spec.objects.get(
                    spec_id=cluster["spec_id_dict"][redis_ip]
                ).get_spec_info()
                act_kwargs.cluster["meta_func_name"] = RedisDBMeta.redis_install.__name__
                acts_list.append(
                    {
                        "act_name": _("Redis-{}-写入元数据").format(redis_ip),
                        "act_component_code": RedisDBMetaComponent.code,
                        "kwargs": asdict(act_kwargs),
                    },
                )
            sub_pipeline.add_parallel_acts(acts_list)

            # 建立主从关系
            act_kwargs.cluster = {
                "repl": cluster["repl_list"],
                "created_by": self.data["created_by"],
                "meta_func_name": RedisDBMeta.replicaof_link.__name__,
            }
            sub_pipeline.add_act(
                act_name=_("redis建立主从 元数据"), act_component_code=RedisDBMetaComponent.code, kwargs=asdict(act_kwargs)
            )

            act_kwargs.cluster = {
                "new_proxy_ips": cluster["proxy_ips"],
                "proxy_port": cluster["proxy_port"],
                "cluster_type": params["clusterinfo"]["cluster_type"],
                "bk_biz_id": self.data["bk_biz_id"],
                "bk_cloud_id": self.data["bk_cloud_id"],
                "cluster_name": params["clusterinfo"]["name"],
                "cluster_alias": params["clusterinfo"]["alias"],
                "db_version": params["clusterinfo"]["db_version"],
                "immute_domain": params["clusterinfo"]["immute_domain"],
                "created_by": self.data["created_by"],
                "region": params["clusterinfo"]["region"],
                "disaster_tolerance_level": self.data.get("disaster_tolerance_level", AffinityEnum.CROS_SUBZONE),
            }

            # 建立集群关系，不同类型走不通方式
            if self.data["db_type"] == ClusterType.TendisPredixyRedisCluster.value:
                storages = [
                    {"ip": ip, "port": port} for ip in cluster["master_ips"] for port in cluster["ip_port_dict"][ip]
                ]
                act_kwargs.cluster["storages"] = storages
                act_kwargs.cluster["meta_func_name"] = RedisDBMeta.redis_origin_make_cluster.__name__
            elif self.data["db_type"] in [
                ClusterType.TwemproxyTendisSSDInstance.value,
                ClusterType.TendisTwemproxyRedisInstance.value,
            ]:
                servers = []
                for ins, seg in cluster["seg_dict"].items():
                    servers.append("{} {} {} {}".format(ins, params["clusterinfo"]["name"], seg, 1))
                act_kwargs.cluster["servers"] = servers
                act_kwargs.cluster["meta_func_name"] = RedisDBMeta.redis_segment_make_cluster.__name__
            else:
                raise Exception(self.data["db_type"] + "is unknown cluster type. please check")
            sub_pipeline.add_act(
                act_name=_(self.data["db_type"] + "建立集群 元数据"),
                act_component_code=RedisDBMetaComponent.code,
                kwargs=asdict(act_kwargs),
            )

            acts_list = []
            for ip in cluster["master_ips"] + cluster["slave_ips"] + cluster["proxy_ips"]:
                act_kwargs.exec_ip = ip
                act_kwargs.cluster = {"ip": ip}
                act_kwargs.get_redis_payload_func = RedisActPayload.bkdbmon_install_list_new.__name__
                acts_list.append(
                    {
                        "act_name": _("{}-安装bkdbmon").format(ip),
                        "act_component_code": ExecuteDBActuatorScriptComponent.code,
                        "kwargs": asdict(act_kwargs),
                    }
                )
            sub_pipeline.add_parallel_acts(acts_list=acts_list)

            db_admin = {"db_type": DBType.Redis.value, "users": str.split(self.data["nosqldbas"], ",")}
            act_kwargs.cluster = {
                "db_admins": [db_admin],
                "meta_func_name": RedisDBMeta.update_nosql_dba.__name__,
            }
            sub_pipeline.add_act(
                act_name=_("更新业务NOSQL DBA"), act_component_code=RedisDBMetaComponent.code, kwargs=asdict(act_kwargs)
            )

            # clb、北极星需要写元数据
            if len(params["entry"]["clb"]) != 0:
                act_kwargs.cluster = params["entry"]["clb"]
                act_kwargs.cluster["bk_cloud_id"] = self.data["bk_cloud_id"]
                act_kwargs.cluster["immute_domain"] = params["clusterinfo"]["immute_domain"]
                act_kwargs.cluster["created_by"] = self.data["created_by"]
                act_kwargs.cluster["meta_func_name"] = RedisDBMeta.add_clb_domain.__name__
                sub_pipeline.add_act(
                    act_name=_("clb元数据写入"), act_component_code=RedisDBMetaComponent.code, kwargs=asdict(act_kwargs)
                )

            if len(params["entry"]["polairs"]) != 0:
                act_kwargs.cluster = params["entry"]["polairs"]
                act_kwargs.cluster["bk_cloud_id"] = self.data["bk_cloud_id"]
                act_kwargs.cluster["immute_domain"] = params["clusterinfo"]["immute_domain"]
                act_kwargs.cluster["created_by"] = self.data["created_by"]
                act_kwargs.cluster["meta_func_name"] = RedisDBMeta.add_polairs_domain.__name__
                sub_pipeline.add_act(
                    act_name=_("polairs元数据写入"), act_component_code=RedisDBMetaComponent.code, kwargs=asdict(act_kwargs)
                )

            # 如果是cluster架构，需要将nodes相关元数据补充。
            if is_redis_cluster_protocal(params["clusterinfo"]["cluster_type"]):
                act_kwargs.cluster = {
                    "nodes_domain": params["clusterinfo"]["nodes_domain"],
                    "immute_domain": params["clusterinfo"]["immute_domain"],
                    "bk_biz_id": self.data["bk_biz_id"],
                    "meta_func_name": RedisDBMeta.update_cluster_entry.__name__,
                }
                sub_pipeline.add_act(
                    act_name=_("更新storageinstance_bind_entry元数据"),
                    act_component_code=RedisDBMetaComponent.code,
                    kwargs=asdict(act_kwargs),
                )

            # 为了把密码写进密码服务里去，写配置需要放在最后来做了
            # 写配置文件 begin
            acts_list = []
            proxy_pwd = ""
            redis_password = ""
            # 处理配置
            params["redis_config"] = self.__check_config(
                str(self.data["bk_biz_id"]),
                params["clusterinfo"]["db_version"],
                ConfType.DBCONF,
                params["clusterinfo"]["cluster_type"],
                params["redis_config"],
            )
            if "requirepass" in params["redis_config"]:
                del params["redis_config"]["requirepass"]
            if "redis_password" in params["proxy_config"]:
                redis_password = params["proxy_config"].pop("redis_password")
            if "password" in params["proxy_config"]:
                proxy_pwd = params["proxy_config"].pop("password")
            params["proxy_config"]["port"] = str(cluster["proxy_port"])

            act_kwargs.cluster = {
                "conf": params["redis_config"],
                "backup_config": params["backup_config"],
                "db_version": params["clusterinfo"]["db_version"],
                "domain_name": params["clusterinfo"]["immute_domain"],
            }
            if (
                params["clusterinfo"]["cluster_type"] == ClusterType.TendisTwemproxyRedisInstance.value
                and params["clusterinfo"]["db_version"] != RedisVersion.Redis20.value
            ):
                act_kwargs.cluster["conf"]["cluster-enabled"] = ClusterStatus.REDIS_CLUSTER_NO
            if params["clusterinfo"]["cluster_type"] == ClusterType.TendisPredixyRedisCluster.value:
                act_kwargs.cluster["conf"]["cluster-enabled"] = ClusterStatus.REDIS_CLUSTER_YES
            act_kwargs.get_redis_payload_func = RedisActPayload.set_redis_config.__name__
            acts_list.append(
                {
                    "act_name": _("回写集群配置[Redis]"),
                    "act_component_code": RedisConfigComponent.code,
                    "kwargs": asdict(act_kwargs),
                },
            )

            act_kwargs.cluster = {
                "conf": params["proxy_config"],
                "pwd_conf": {
                    "proxy_pwd": proxy_pwd,
                    "proxy_admin_pwd": proxy_pwd,
                    "redis_pwd": redis_password,
                },
                "domain_name": params["clusterinfo"]["immute_domain"],
            }
            act_kwargs.get_redis_payload_func = RedisActPayload.set_proxy_config.__name__
            acts_list.append(
                {
                    "act_name": _("回写集群proxy配置"),
                    "act_component_code": RedisConfigComponent.code,
                    "kwargs": asdict(act_kwargs),
                }
            )
            sub_pipeline.add_parallel_acts(acts_list)

            # 历史备份记录上报
            upload_backup_sub_pipelines = []
            for redis_ip in cluster["slave_ips"]:
                upload_backup_sub_pipelines.append(
                    RedisReuploadOldBackupRecordsAtomJob(
                        self.root_id,
                        self.data,
                        act_kwargs,
                        {
                            "bk_biz_id": self.data["bk_biz_id"],
                            "bk_cloud_id": self.data["bk_cloud_id"],
                            "server_ip": redis_ip,
                            "server_ports": cluster["ip_port_dict"][redis_ip],
                            "cluster_domain": params["clusterinfo"]["immute_domain"],
                            "cluster_type": params["clusterinfo"]["cluster_type"],
                            "meta_role": InstanceRole.REDIS_SLAVE.value,
                            "server_shards": cluster["server_shards"][redis_ip],
                        },
                    )
                )
            sub_pipeline.add_parallel_sub_pipeline(upload_backup_sub_pipelines)
            # 写配置文件 end

            sub_pipelines.append(
                sub_pipeline.build_sub_process(sub_name=_("{}迁移子任务").format(params["clusterinfo"]["immute_domain"]))
            )
        redis_pipeline.add_parallel_sub_pipeline(sub_flow_list=sub_pipelines)
        redis_pipeline.run_pipeline()


class RedisInsMigrateLoadFlow(object):
    """
    redis 单实例 迁移元数据
    """

    def __init__(self, root_id: str, data: Optional[Dict]):
        """
        @param root_id : 任务流程定义的root_id
        @param data : 单据传递过来的参数列表，是dict格式
        """
        self.root_id = root_id
        self.data = data

    def __get_old_ins_info(self, ip: str) -> dict:
        """
        获取ip相关的老实例信息
        ports/slave_ip/db_version
        """
        ports = []
        slave_ip = ""
        db_version = ""
        clusters = query_cluster_by_hosts([ip])
        if len(clusters) != 0:
            ports = clusters[0]["ports"]
            db_version = clusters[0]["major_version"]

            storages = [{"ip": ip, "port": ports[0]}]
            storage_objs = common.filter_out_instance_obj(storages, StorageInstance.objects.all())
            slave_objs = storage_objs.get(instance_inner_role=InstanceInnerRole.MASTER).as_ejector.get().receiver
            slave_ip = slave_objs.machine.ip
        return {
            "ports": ports,
            "slave_ip": slave_ip,
            "db_version": db_version,
        }

    def __dispose_cluster_params(self, cluster_info: dict, ignore_check: bool = False) -> dict:
        """
        处理参数
        返回需要的处理后的数据格式
        """

        master_ip_list = []
        old_ports_dict = defaultdict(list)  # ip对应历史已安装端口
        new_ports_dict = defaultdict(list)  # ip对应需要新安装端口
        db_version_dict = {}  # ip对应的版本
        spec_id_dict = {}  # 机器对应规格
        repl_dict = {}  # ip主从复制关系
        ip_install_dict = defaultdict(list)

        for ins in cluster_info["tendis_instance"]:
            master_ip = ins["backends"]["master"]["ip"]
            slave_ip = ins["backends"]["slave"]["ip"]
            port = ins["backends"]["master"]["port"]
            spec_id = ins["backends"]["master"]["spec_id"]
            db_version = ins["clusterinfo"]["db_version"]

            if master_ip not in master_ip_list:
                master_ip_list.append(master_ip)
                repl_dict[master_ip] = slave_ip
                spec_id_dict[master_ip] = spec_id
                db_version_dict[master_ip] = db_version

                machine_old_info = self.__get_old_ins_info(master_ip)
                if len(machine_old_info["ports"]):
                    old_ports_dict[master_ip] = machine_old_info["ports"]
                    if not ignore_check:
                        if machine_old_info["slave_ip"] != slave_ip:
                            raise Exception(master_ip + " old slave is: " + machine_old_info["slave_ip"])
                        if machine_old_info["db_version"] != db_version:
                            raise Exception(master_ip + " old db_version is: " + machine_old_info["db_version"])
            if not ignore_check:
                if db_version != db_version_dict[master_ip]:
                    raise Exception(master_ip + " have more db_version")
                if slave_ip != repl_dict[master_ip]:
                    raise Exception("master have more slave")
                if port in new_ports_dict[master_ip]:
                    raise Exception(master_ip + " port have conflict: " + str(port))
                if port in old_ports_dict[master_ip]:
                    raise Exception(master_ip + " port is exists: " + str(port))
            new_ports_dict[master_ip].append(port)
            ip_install_dict[master_ip].append(ins)

        return {
            "master_ip_list": master_ip_list,
            "new_ports_dict": dict(new_ports_dict),
            "spec_id_dict": spec_id_dict,
            "db_version_dict": db_version_dict,
            "old_ports_dict": dict(old_ports_dict),
            "repl_dict": repl_dict,
            "ip_install_dict": dict(ip_install_dict),
        }

    def redis_ins_migrate_load_flow(self):
        redis_pipeline = Builder(root_id=self.root_id, data=self.data)
        act_kwargs = ActKwargs()
        act_kwargs.set_trans_data_dataclass = CommonContext.__name__
        act_kwargs.is_update_trans_data = True
        act_kwargs.bk_cloud_id = self.data["bk_cloud_id"]
        ins_status = InstanceStatus.UNAVAILABLE
        ignore_check = True
        if self.data["migrate_ctl"]["meta"]:
            ignore_check = False
        if self.data["migrate_ctl"]["dbha"]:
            ins_status = InstanceStatus.RUNNING
        info = self.__dispose_cluster_params(self.data, ignore_check)
        sub_pipelines = []
        for master_ip in info["ip_install_dict"]:
            old_ports = info["old_ports_dict"][master_ip]
            db_version = info["db_version_dict"][master_ip]
            slave_ip = info["repl_dict"][master_ip]
            all_ip = [master_ip, slave_ip]
            spec_id = info["spec_id_dict"][master_ip]

            act_kwargs.cluster["db_version"] = db_version
            act_kwargs.cluster["cluster_type"] = ClusterType.TendisRedisInstance.value
            sub_pipeline = SubBuilder(root_id=self.root_id, data=self.data)

            if ins_status == InstanceStatus.RUNNING and not self.data["migrate_ctl"]["meta"]:
                acts_list = []
                for redis_ip in all_ip:
                    act_kwargs.cluster["meta_update_ip"] = redis_ip
                    act_kwargs.cluster["meta_update_ports"] = info["new_ports_dict"][master_ip]
                    act_kwargs.cluster["meta_update_status"] = InstanceStatus.RUNNING
                    act_kwargs.cluster["meta_func_name"] = RedisDBMeta.instances_status_update.__name__
                    acts_list.append(
                        {
                            "act_name": _("{}-更新redis状态".format(redis_ip)),
                            "act_component_code": RedisDBMetaComponent.code,
                            "kwargs": asdict(act_kwargs),
                        },
                    )
                sub_pipeline.add_parallel_acts(acts_list)
                sub_pipelines.append(sub_pipeline.build_sub_process(sub_name=_("{}更新状态子任务").format(master_ip)))
                continue

            if not self.data["migrate_ctl"]["meta"]:
                continue

            # 初始化配置
            sub_pipeline.add_act(
                act_name=_("初始化配置"), act_component_code=GetRedisActPayloadComponent.code, kwargs=asdict(act_kwargs)
            )

            # 下发介质包
            trans_files = GetFileList(db_type=DBType.Redis)
            act_kwargs.file_list = trans_files.redis_cluster_apply_backend(db_version)
            act_kwargs.exec_ip = all_ip
            sub_pipeline.add_act(
                act_name=_("Redis-{}-下发介质包").format(all_ip),
                act_component_code=TransFileComponent.code,
                kwargs=asdict(act_kwargs),
            )

            if len(old_ports) == 0:
                "如果之前没有安装过实例，则需要做初始化和安装工具操作"
                act_kwargs.get_redis_payload_func = RedisActPayload.get_sys_init_payload.__name__
                sub_pipeline.add_act(
                    act_name=_("Redis-{}-初始化机器").format(all_ip),
                    act_component_code=ExecuteDBActuatorScriptComponent.code,
                    kwargs=asdict(act_kwargs),
                )

                acts_list = []
                acts_list.append(
                    {
                        "act_name": _("Redis-{}-安装backup-client工具").format(all_ip),
                        "act_component_code": DownloadBackupClientComponent.code,
                        "kwargs": asdict(
                            DownloadBackupClientKwargs(
                                bk_cloud_id=self.data["bk_cloud_id"],
                                bk_biz_id=int(self.data["bk_biz_id"]),
                                download_host_list=all_ip,
                            ),
                        ),
                    }
                )
                for plugin_name in DEPENDENCIES_PLUGINS:
                    acts_list.append(
                        {
                            "act_name": _("安装[{}]插件".format(plugin_name)),
                            "act_component_code": InstallNodemanPluginServiceComponent.code,
                            "kwargs": asdict(
                                InstallNodemanPluginKwargs(
                                    bk_cloud_id=int(self.data["bk_cloud_id"]), ips=all_ip, plugin_name=plugin_name
                                )
                            ),
                        }
                    )
                sub_pipeline.add_parallel_acts(acts_list=acts_list)

            # 写入元数据
            act_kwargs.cluster["spec_id"] = spec_id
            act_kwargs.cluster["spec_config"] = Spec.objects.get(spec_id=spec_id).get_spec_info()
            act_kwargs.cluster["ports"] = info["new_ports_dict"][master_ip]
            act_kwargs.cluster["meta_func_name"] = RedisDBMeta.redis_install_append.__name__
            act_kwargs.cluster["master_ip"] = master_ip
            act_kwargs.cluster["slave_ip"] = slave_ip
            act_kwargs.cluster["ins_status"] = ins_status
            sub_pipeline.add_act(
                act_name=_("Redis-{}-写入元数据").format(master_ip),
                act_component_code=RedisDBMetaComponent.code,
                kwargs=asdict(act_kwargs),
            )
            # 建立主从元数据
            replica_pairs = []
            for ins in info["ip_install_dict"][master_ip]:
                replica_pairs.append(
                    {
                        "master_ip": master_ip,
                        "master_port": ins["backends"]["master"]["port"],
                        "master_auth": ins["config"]["requirepass"],
                        "slave_ip": info["repl_dict"][master_ip],
                        "slave_port": ins["backends"]["slave"]["port"],
                        "slave_password": ins["config"]["requirepass"],
                    }
                )
            act_kwargs.cluster = {
                "bacth_pairs": replica_pairs,
                "created_by": self.data["created_by"],
                "meta_func_name": RedisDBMeta.replicaof_ins.__name__,
            }
            sub_pipeline.add_act(
                act_name=_("redis建立主从 元数据"), act_component_code=RedisDBMetaComponent.code, kwargs=asdict(act_kwargs)
            )

            # 主从集群元数据
            acts_list = []
            for ins in info["ip_install_dict"][master_ip]:
                act_kwargs.cluster = {
                    "bk_biz_id": self.data["bk_biz_id"],
                    "bk_cloud_id": self.data["bk_cloud_id"],
                    "cluster_name": ins["clusterinfo"]["name"],
                    "cluster_alias": ins["clusterinfo"]["alias"],
                    "db_version": ins["clusterinfo"]["db_version"],
                    "immute_domain": ins["clusterinfo"]["immute_domain"],
                    "master_ip": master_ip,
                    "slave_ip": slave_ip,
                    "port": ins["backends"]["master"]["port"],
                    "created_by": self.data["created_by"],
                    "region": ins["clusterinfo"]["region"],
                    "meta_func_name": RedisDBMeta.redis_instance.__name__,
                    "disaster_tolerance_level": self.data.get("disaster_tolerance_level", AffinityEnum.CROS_SUBZONE),
                }
                acts_list.append(
                    {
                        "act_name": _("{}-主从实例集群元数据").format(ins["clusterinfo"]["immute_domain"]),
                        "act_component_code": RedisDBMetaComponent.code,
                        "kwargs": asdict(act_kwargs),
                    },
                )
            sub_pipeline.add_parallel_acts(acts_list=acts_list)

            db_admin = {"db_type": DBType.Redis.value, "users": str.split(self.data["nosqldbas"], ",")}
            act_kwargs.cluster = {
                "db_admins": [db_admin],
                "meta_func_name": RedisDBMeta.update_nosql_dba.__name__,
            }
            sub_pipeline.add_act(
                act_name=_("更新业务NOSQL DBA"), act_component_code=RedisDBMetaComponent.code, kwargs=asdict(act_kwargs)
            )

            # 写config，需要在写集群元数据后面
            acts_list = []
            for ins in info["ip_install_dict"][master_ip]:
                act_kwargs.cluster = {
                    "pwd_conf": {
                        "redis_pwd": ins["config"].pop("requirepass"),
                    },
                    "conf": ins["config"],
                    "db_version": ins["clusterinfo"]["db_version"],
                    "domain_name": ins["clusterinfo"]["immute_domain"],
                }
                if (
                    ins["clusterinfo"]["cluster_type"] == ClusterType.TendisRedisInstance.value
                    and ins["clusterinfo"]["db_version"] != RedisVersion.Redis20.value
                ):
                    act_kwargs.cluster["conf"]["cluster-enabled"] = ClusterStatus.REDIS_CLUSTER_NO

                act_kwargs.get_redis_payload_func = RedisActPayload.set_redis_config.__name__
                acts_list.append(
                    {
                        "act_name": _("{}-回写集群配置[Redis]").format(ins["clusterinfo"]["immute_domain"]),
                        "act_component_code": RedisConfigComponent.code,
                        "kwargs": asdict(act_kwargs),
                    },
                )
            sub_pipeline.add_parallel_acts(acts_list=acts_list)

            # 部署bkdbmon
            acts_list = []
            act_kwargs.exec_ip = master_ip
            act_kwargs.cluster = {
                "ip": master_ip,
            }
            act_kwargs.get_redis_payload_func = RedisActPayload.bkdbmon_install_list_new.__name__
            acts_list.append(
                {
                    "act_name": _("{}-安装bkdbmon").format(master_ip),
                    "act_component_code": ExecuteDBActuatorScriptComponent.code,
                    "kwargs": asdict(act_kwargs),
                }
            )
            act_kwargs.exec_ip = slave_ip
            act_kwargs.cluster = {
                "ip": slave_ip,
            }
            act_kwargs.get_redis_payload_func = RedisActPayload.bkdbmon_install_list_new.__name__
            acts_list.append(
                {
                    "act_name": _("{}-安装bkdbmon").format(slave_ip),
                    "act_component_code": ExecuteDBActuatorScriptComponent.code,
                    "kwargs": asdict(act_kwargs),
                }
            )
            sub_pipeline.add_parallel_acts(acts_list=acts_list)

            # 历史备份记录上报
            upload_backup_sub_pipelines = []
            for ins in info["ip_install_dict"][master_ip]:
                upload_backup_sub_pipelines.append(
                    RedisReuploadOldBackupRecordsAtomJob(
                        self.root_id,
                        self.data,
                        act_kwargs,
                        {
                            "bk_biz_id": self.data["bk_biz_id"],
                            "bk_cloud_id": self.data["bk_cloud_id"],
                            "server_ip": slave_ip,
                            "server_ports": [ins["backends"]["master"]["port"]],
                            "cluster_domain": ins["clusterinfo"]["immute_domain"],
                            "cluster_type": ins["clusterinfo"]["cluster_type"],
                            "meta_role": InstanceRole.REDIS_SLAVE.value,
                            "server_shards": {},
                        },
                    )
                )
            sub_pipeline.add_parallel_sub_pipeline(upload_backup_sub_pipelines)

            # clb、北极星需要写元数据
            for ins in info["ip_install_dict"][master_ip]:
                if len(ins["entry"]["clb"]) != 0:
                    act_kwargs.cluster = ins["entry"]["clb"]
                    act_kwargs.cluster["bk_cloud_id"] = self.data["bk_cloud_id"]
                    act_kwargs.cluster["immute_domain"] = ins["clusterinfo"]["immute_domain"]
                    act_kwargs.cluster["created_by"] = self.data["created_by"]
                    act_kwargs.cluster["meta_func_name"] = RedisDBMeta.add_clb_domain.__name__
                    sub_pipeline.add_act(
                        act_name=_("clb元数据写入"), act_component_code=RedisDBMetaComponent.code, kwargs=asdict(act_kwargs)
                    )

                if len(ins["entry"]["polairs"]) != 0:
                    act_kwargs.cluster = ins["entry"]["polairs"]
                    act_kwargs.cluster["bk_cloud_id"] = self.data["bk_cloud_id"]
                    act_kwargs.cluster["immute_domain"] = ins["clusterinfo"]["immute_domain"]
                    act_kwargs.cluster["created_by"] = self.data["created_by"]
                    act_kwargs.cluster["meta_func_name"] = RedisDBMeta.add_polairs_domain.__name__
                    sub_pipeline.add_act(
                        act_name=_("polairs元数据写入"),
                        act_component_code=RedisDBMetaComponent.code,
                        kwargs=asdict(act_kwargs),
                    )

            sub_pipelines.append(sub_pipeline.build_sub_process(sub_name=_("{}迁移子任务").format(master_ip)))
        redis_pipeline.add_parallel_sub_pipeline(sub_flow_list=sub_pipelines)
        redis_pipeline.run_pipeline()
