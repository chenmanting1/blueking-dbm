/*
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-DB管理系统(BlueKing-BK-DBM) available.
 * Copyright (C) 2017-2023 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at https://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

// Package mysqlcmd TODO
package mysqlcmd

import (
	"dbm-services/mysql/db-tools/dbactuator/internal/subcmd"
	"dbm-services/mysql/db-tools/dbactuator/pkg/util/templates"

	"github.com/spf13/cobra"
)

// NewMysqlCommand mysql子命令
func NewMysqlCommand() *cobra.Command {
	cmds := &cobra.Command{
		Use:   "mysql [mysql operation]",
		Short: "MySQL Operation Command Line Interface",
		RunE:  subcmd.ValidateSubCommand(),
	}
	groups := templates.CommandGroups{
		{
			Message: "mysql operation sets",
			Commands: []*cobra.Command{
				NewDeployMySQLInstanceCommand(),
				NewUnInstallMysqlCommand(),
				NewGrantReplCommand(),
				NewExecSQLFileCommand(),
				CloneClientGrantCommand(),
				//NewBackupTruncateDatabaseCommand(),
				NewUpgradeMySQLCommand(),
				// NewBackupDatabaseTableCommand(),
				MycnfChangeCommand(),
				FindLocalBackupCommand(),
				MycnfCloneCommand(),
				NewCutOverToSlaveCommnad(),
				CleanMysqlCommand(),
				PtTableSyncCommand(),
				ParseBinlogTimeCommand(),
				FlashbackBinlogCommand(),
				NewPtTableChecksumCommand(),
				NewInstallMySQLChecksumCommand(),
				NewInstallNewDbBackupCommand(),
				// NewFullBackupCommand(),
				NewInstallRotateBinlogCommand(),
				NewInstallDBAToolkitCommand(),
				NewDeployMySQLCrondCommand(),
				ClearInstanceConfigCommand(),
				NewInstallMySQLMonitorCommand(),
				NewExecPartitionSQLCommand(),
				NewBackupDemandCommand(),
				NewDropTableCommand(),
				InstallBackupClientCommand(),
				NewEnableTokudbPluginCommand(),
				NewOpenAreaDumpSchemaCommand(),
				NewOpenAreaImportSchemaCommand(),
				NewOpenAreaDumpData(),
				NewOpenAreaImportData(),
				OSCmdRunCommand(),
				OSInfoGetCommand(),
				NewStandardizeMySQLCommand(),
				NewStandardizeProxyCommand(),
				NewMysqlDataMigrateDumpCommand(),
				NewMysqlDataMigrateImportCommand(),
				NewDbConsoleDumpCommand(),
				NewTruncatePreDropStageOnRemoteCommand(),
				NewTruncateOnMySQLCommand(),
				NewRenameOnMySQLCommand(),
				NewTruncateDBsInUsingCommand(),
				NewRenameDBsInUsingCommand(),
				NewRenamePreDropToOnRemoteCommand(),
			},
		},
		{
			Message: "mysql semantic check operation sets",
			Commands: []*cobra.Command{
				NewSenmanticDumpSchemaCommand(),
			},
		},
		{
			Message: "mysql slave operation  sets",
			Commands: []*cobra.Command{
				NewBuildMsRelatioCommand(),
				RestoreDRCommand(),
				RecoverBinlogCommand(),
			},
		},
	}
	groups.Add(cmds)
	return cmds
}
