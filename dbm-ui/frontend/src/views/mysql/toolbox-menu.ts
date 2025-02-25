/*
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-DB管理系统(BlueKing-BK-DBM) available.
 *
 * Copyright (C) 2017-2023 THL A29 Limited, a Tencent company. All rights reserved.
 *
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at https://opensource.org/licenses/MIT
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
 * the specific language governing permissions and limitations under the License.
 */

import { t } from '@locales/index';

export interface MenuChild {
  name: string;
  id: string;
  parentId: string;
  dbConsoleValue: string;
}

export default [
  {
    name: t('SQL任务'),
    id: 'sql',
    icon: 'db-icon-mysql',
    children: [
      {
        name: t('变更SQL执行'),
        id: 'MySQLExecute',
        parentId: 'sql',
        dbConsoleValue: 'mysql.toolbox.sqlExecute',
      },
      {
        name: t('DB重命名'),
        id: 'MySQLDBRename',
        parentId: 'sql',
        dbConsoleValue: 'mysql.toolbox.dbRename',
      },
    ],
  },
  {
    name: t('备份'),
    id: 'copy',
    icon: 'db-icon-copy',
    children: [
      {
        name: t('库表备份'),
        id: 'MySQLDBTableBackup',
        parentId: 'copy',
        dbConsoleValue: 'mysql.toolbox.dbTableBackup',
      },
      {
        name: t('全库备份'),
        id: 'MySQLDBBackup',
        parentId: 'copy',
        dbConsoleValue: 'mysql.toolbox.dbBackup',
      },
    ],
  },
  {
    name: t('回档'),
    id: 'fileback',
    icon: 'db-icon-rollback',
    children: [
      {
        name: t('定点构造'),
        id: 'MySQLDBRollback',
        parentId: 'fileback',
        dbConsoleValue: 'mysql.toolbox.rollback',
      },
      {
        name: t('闪回'),
        id: 'MySQLDBFlashback',
        parentId: 'fileback',
        dbConsoleValue: 'mysql.toolbox.flashback',
      },
    ],
  },
  {
    name: t('权限克隆'),
    id: 'privilege',
    icon: 'db-icon-clone',
    children: [
      {
        name: t('客户端权限克隆'),
        id: 'MySQLPrivilegeCloneClient',
        parentId: 'privilege',
        dbConsoleValue: 'mysql.toolbox.clientPermissionClone',
      },
      {
        name: t('DB实例权限克隆'),
        id: 'MySQLPrivilegeCloneInst',
        parentId: 'privilege',
        dbConsoleValue: 'mysql.toolbox.dbInstancePermissionClone',
      },
    ],
  },
  {
    name: t('集群维护'),
    id: 'migrate',
    icon: 'db-icon-cluster',
    children: [
      {
        name: t('重建从库'),
        id: 'MySQLSlaveRebuild',
        parentId: 'migrate',
        dbConsoleValue: 'mysql.toolbox.slaveRebuild',
      },
      {
        name: t('添加从库'),
        id: 'MySQLSlaveAdd',
        parentId: 'migrate',
        dbConsoleValue: 'mysql.toolbox.slaveAdd',
      },
      {
        name: t('迁移主从'),
        id: 'MySQLMasterSlaveClone',
        parentId: 'migrate',
        dbConsoleValue: 'mysql.toolbox.masterSlaveClone',
      },
      {
        name: t('主从互切'),
        id: 'MySQLMasterSlaveSwap',
        parentId: 'migrate',
        dbConsoleValue: 'mysql.toolbox.masterSlaveSwap',
      },
      {
        name: t('替换Proxy'),
        id: 'MySQLProxyReplace',
        parentId: 'migrate',
        dbConsoleValue: 'mysql.toolbox.proxyReplace',
      },
      {
        name: t('添加Proxy'),
        id: 'MySQLProxyAdd',
        parentId: 'migrate',
        dbConsoleValue: 'mysql.toolbox.proxyAdd',
      },
      {
        name: t('主库故障切换'),
        id: 'MySQLMasterFailover',
        parentId: 'migrate',
        dbConsoleValue: 'mysql.toolbox.masterFailover',
      },
      {
        name: t('版本升级'),
        id: 'MySQLVersionUpgrade',
        parentId: 'migrate',
        dbConsoleValue: 'mysql.toolbox.versionUpgrade',
      },
    ],
  },
  {
    name: t('数据处理'),
    id: 'data',
    icon: 'db-icon-data',
    children: [
      {
        name: t('清档'),
        id: 'MySQLDBClear',
        parentId: 'data',
        dbConsoleValue: 'mysql.toolbox.dbClear',
      },
      {
        name: t('数据校验修复'),
        id: 'MySQLChecksum',
        parentId: 'data',
        dbConsoleValue: 'mysql.toolbox.checksum',
      },
      {
        name: t('DB克隆'),
        id: 'MySQLDataMigrate',
        parentId: 'data',
        dbConsoleValue: 'mysql.toolbox.dataMigrate',
      },
    ],
  },
  {
    name: t('克隆开区'),
    id: 'mysql_openarea',
    icon: 'db-icon-template',
    children: [
      {
        name: t('开区模版'),
        id: 'MySQLOpenareaTemplate',
        parentId: 'mysql_openarea',
        dbConsoleValue: 'mysql.toolbox.openareaTemplate',
      },
    ],
  },
  {
    name: t('数据查询'),
    id: 'mysql_data_query',
    icon: 'db-icon-search',
    children: [
      {
        name: 'Webconsole',
        id: 'MySQLWebconsole',
        parentId: 'mysql_data_query',
        dbConsoleValue: 'mysql.toolbox.webconsole',
      },
    ],
  },
];
