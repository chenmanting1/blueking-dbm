/*
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-DB管理系统(BlueKing-BK-DBM) available.
 * Copyright (C) 2017-2023 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at https://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

package mysqlcmd

import (
	"fmt"

	"github.com/spf13/cobra"

	"dbm-services/bigdata/db-tools/dbactuator/pkg/util"
	"dbm-services/common/go-pubpkg/logger"
	"dbm-services/mysql/db-tools/dbactuator/internal/subcmd"
	"dbm-services/mysql/db-tools/dbactuator/pkg/components/mysql"
)

// DbConsoleDumpAct dump action
type DbConsoleDumpAct struct {
	*subcmd.BaseOptions
	Service mysql.DbConsoleDumpComp
}

// NewDbConsoleDumpCommand create new subcommand
func NewDbConsoleDumpCommand() *cobra.Command {
	act := DbConsoleDumpAct{
		BaseOptions: subcmd.GBaseOptions,
	}
	cmd := &cobra.Command{
		Use:   "dump",
		Short: "运行导出SQL文件",
		Example: fmt.Sprintf(
			`dbactuator mysql dump %s %s`,
			subcmd.CmdBaseExampleStr, subcmd.ToPrettyJson(act.Service.Example()),
		),
		Run: func(cmd *cobra.Command, args []string) {
			util.CheckErr(act.Validate())
			util.CheckErr(act.Init())
			util.CheckErr(act.Run())
		},
	}
	return cmd
}

// Validate run selfdefine validate function
func (d *DbConsoleDumpAct) Validate() (err error) {
	return d.BaseOptions.Validate()
}

// Init prepare run env
func (d *DbConsoleDumpAct) Init() (err error) {
	if err = d.Deserialize(&d.Service.Params); err != nil {
		logger.Error("DeserializeAndValidate failed, %v", err)
		return err
	}
	d.Service.GeneralParam = subcmd.GeneralRuntimeParam
	return nil
}

// Run Command Run
func (d *DbConsoleDumpAct) Run() (err error) {
	steps := subcmd.Steps{
		{
			FunName: "初始化",
			Func:    d.Service.Init,
		},
		{
			FunName: "运行数据导出",
			Func:    d.Service.Run,
		},
		{
			FunName: "上传制品库",
			Func:    d.Service.Upload,
		},
	}
	if err := steps.Run(); err != nil {
		return err
	}

	logger.Info("导出数据成功")
	return nil
}
