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
import logging
from collections import defaultdict
from datetime import datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone

from backend.db_meta.enums import ClusterType
from backend.db_meta.models import Cluster
from backend.db_report.enums import MysqlBackupCheckSubType
from backend.db_report.models import MysqlBackupCheckReport

from .bklog_query import ClusterBackup

logger = logging.getLogger("root")


def get_query_date_time(date_str: str):
    # date_str 为空时，取当前时间的前一天为查询区间，不为空时需要是 2024-05-20 这样的格式，指定查询这一天 00:00:01-23:59:59 的数据
    # 指定时间，一般用于手动触发使用
    if date_str == "":
        date_object = datetime.now() - timedelta(days=1)  # 当前时区
        start_of_day = datetime.combine(date_object, time.min).astimezone(timezone.utc)
        end_of_day = datetime.combine(date_object, time.max).astimezone(timezone.utc)
        return start_of_day, end_of_day
    else:
        date_object = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_of_day = datetime(date_object.year, date_object.month, date_object.day).astimezone(timezone.utc)
        end_of_day = datetime(date_object.year, date_object.month, date_object.day, 23, 59, 59).astimezone(
            timezone.utc
        )
        return start_of_day, end_of_day


def check_full_backup(date_str: str):
    # tendbha 全备巡检
    _check_tendbha_full_backup(date_str)
    # tendbcluster 全备巡检
    _check_tendbcluster_full_backup(date_str)


class BackupFile:
    def __init__(self, file_name: str, file_size: int, file_type="", task_id=""):
        self.file_name = file_name
        self.file_size = file_size
        self.file_type = file_type
        self.backup_task_id = task_id


class MysqlBackup:
    def __init__(self, cluster_id: int, cluster_domain: str, backup_id=""):
        self.cluster_id = cluster_id
        self.cluster_domain = cluster_domain
        self.backup_id = backup_id
        self.backup_type = ""
        self.backup_role = ""
        self.is_full_backup = 0
        self.data_schema_grant = ""
        self.consistent_backup_time = ""
        self.shard_value = -1
        self.file_index = None
        self.file_priv = None
        self.file_tar = []


def _build_backup_info_files(backups_info: []):
    backups = {}
    for i in backups_info:
        if i.get("is_full_backup", 0) == 0:
            continue
        bid = "{}#{}".format(i.get("backup_id"), i.get("shard_value"))
        if bid not in backups:
            backups[bid] = MysqlBackup(i["cluster_id"], i["cluster_domain"], i["backup_id"])

        backups[bid].is_full_backup = i.get("is_full_backup")
        for f in i.get("file_list", []):
            file_type = f.get("file_type")
            bf = BackupFile(f.get("file_name"), f.get("file_size"), file_type, f.get("task_id"))
            if file_type == "index":
                backups[bid].file_index = bf
            elif file_type == "priv":
                backups[bid].file_priv = bf
            elif file_type == "tar" or file_type == "part":
                backups[bid].file_tar.append(bf)
            else:
                pass
    return backups


def _check_tendbha_full_backup(date_str: str):
    """
    tendbha 必须有一份完整的备份
    """

    # 清理过期的报表
    MysqlBackupCheckReport.objects.filter(create_at__lte=timezone.now() - timedelta(days=60)).delete()

    # 检查前一天的全备
    start_time, end_time = get_query_date_time(date_str)
    logger.info(
        "====  start check full backup for cluster type {}, time range[{},{}] ====".format(
            ClusterType.TenDBHA, start_time, end_time
        )
    )
    query = Q(cluster_type=ClusterType.TenDBHA) & Q(create_at__lt=timezone.now() - timedelta(days=1))
    for c in Cluster.objects.filter(query):
        logger.info("==== start check full backup for cluster {} ====".format(c.immute_domain))
        backup = ClusterBackup(c.id, c.immute_domain)

        items = backup.query_backup_log_from_bklog(start_time, end_time)
        backup.backups = _build_backup_info_files(items)

        for bid, bk in backup.backups.items():
            if bk.is_full_backup == 1:
                if bk.file_index and bk.file_tar:
                    backup.success = True
                    break
        if not backup.success:
            MysqlBackupCheckReport.objects.create(
                bk_biz_id=c.bk_biz_id,
                bk_cloud_id=c.bk_cloud_id,
                cluster=c.immute_domain,
                cluster_type=ClusterType.TenDBHA,
                status=False,
                msg="no success full backup found",
                subtype=MysqlBackupCheckSubType.FullBackup.value,
            )


def _check_tendbcluster_full_backup(date_str: str):
    """
    tendbcluster 集群必须有完整的备份
    """
    start_time, end_time = get_query_date_time(date_str)
    logger.info(
        "==== start check full backup for cluster type {}, time range[{},{}] ====".format(
            ClusterType.TenDBCluster, start_time, end_time
        )
    )

    for c in Cluster.objects.filter(cluster_type=ClusterType.TenDBCluster):
        logger.info("==== start check full backup for cluster {} ====".format(c.immute_domain))
        backup = ClusterBackup(c.id, c.immute_domain)
        items = backup.query_backup_log_from_bklog(start_time, end_time)
        backup.backups = _build_backup_info_files(items)

        backup_id_stat = defaultdict(list)
        backup_id_invalid = {}
        for bid, bk in backup.backups.items():
            backup_id, shard_id = bid.split("#", 1)
            if bk.is_full_backup == 1:
                if bk.file_index and bk.file_tar:
                    #  这一个 shard ok
                    backup_id_stat[backup_id].append({shard_id: True})
                else:
                    # 这一个 shard 不ok，整个backup_id 无效
                    backup_id_invalid[backup_id] = True
                    backup_id_stat[backup_id].append({shard_id: False})
        message = ""
        for backup_id, stat in backup_id_stat.items():
            if backup_id not in backup_id_invalid:
                backup.success = True
                message = "shard_id:{}".format(backup_id_stat[backup_id])
                break

        # 只记录失败的结果
        if not backup.success:
            MysqlBackupCheckReport.objects.create(
                bk_biz_id=c.bk_biz_id,
                bk_cloud_id=c.bk_cloud_id,
                cluster=c.immute_domain,
                cluster_type=ClusterType.TenDBCluster,
                status=False,
                msg="no success full backup found:{}".format(message),
                subtype=MysqlBackupCheckSubType.FullBackup.value,
            )
