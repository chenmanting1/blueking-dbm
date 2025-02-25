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
from typing import List

from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

# import backend.flow.utils.mongodb.mongodb_dataclass as flow_context
from backend.flow.plugins.components.collections.common.base_service import BaseService
from backend.flow.utils.mongodb.mongodb_password import MongoDBPassword

logger = logging.getLogger("json")


class ExecAddPasswordToDBOperation(BaseService):
    """
    NameServiceCreate服务
    """

    def _execute(self, data, parent_data) -> bool:
        """
        执行创建名字服务功能的函数
        global_data 单据全局变量，格式字典
        kwargs 私有变量
        """

        # 从流程节点中获取变量
        kwargs = data.get_one_of_inputs("kwargs")
        trans_data = data.get_one_of_inputs("trans_data")
        usernames = kwargs["usernames"]

        # if trans_data is None or trans_data == "${trans_data}":
        #     # 表示没有加载上下文内容，则在此添加
        #     trans_data = getattr(flow_context, kwargs["set_trans_data_dataclass"])()

        # 把密码写入db
        for username in usernames:
            if kwargs.get("create", True):
                if kwargs["set_name"]:
                    password = trans_data[kwargs["set_name"]][username]
                else:
                    password = trans_data[username]
            else:
                password = kwargs["passwords"][username]
            result = MongoDBPassword().save_password_to_db(
                instances=kwargs["nodes"], username=username, password=password, operator=kwargs["operator"]
            )
            if result:
                self.log_error("add password of user:{} to db fail, error:{}".format(username, result))
                return False
        self.log_info("add password of users:{} to db successfully".format(",".join(usernames)))
        return True

    # 流程节点输入参数
    def inputs_format(self) -> List:
        return [
            Service.InputItem(name="kwargs", key="kwargs", type="dict", required=True),
            Service.InputItem(name="global_data", key="global_data", type="dict", required=True),
        ]


class ExecAddPasswordToDBOperationComponent(Component):
    """
    ExecAddPasswordToDBOperation组件
    """

    name = __name__
    code = "add_password_to_db"
    bound_service = ExecAddPasswordToDBOperation
