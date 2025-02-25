<!--
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-DB管理系统(BlueKing-BK-DBM) available.
 *
 * Copyright (C) 2017-2023 THL A29 Limited, a Tencent company. All rights reserved.
 *
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License athttps://opensource.org/licenses/MIT
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
 * the specific language governing permissions and limitations under the License.
-->

<template>
  <DbOriginalTable
    class="target-cluster-table"
    :columns="columns"
    :data="tableData" />
</template>

<script setup lang="tsx">
  import _ from 'lodash';
  import { useI18n } from 'vue-i18n';

  import type { MysqlOpenAreaDetails } from '@services/model/ticket/details/mysql';
  import TicketModel from '@services/model/ticket/ticket';

  import { useCopy } from '@hooks';

  interface Props {
    ticketDetails: TicketModel<MysqlOpenAreaDetails>;
  }

  interface RowData {
    targetCluster: string;
    newDb: string;
    ips: string[];
  }

  const props = defineProps<Props>();

  const { t } = useI18n();
  const copy = useCopy();

  const clustersMap = props.ticketDetails.details.clusters;
  const rulesSetMap = props.ticketDetails.details.rules_set.reduce<Record<string, MysqlOpenAreaDetails['rules_set'][number]>>(
    (results, item) => Object.assign(results, {
      [item.target_instances[0]]: item
    }),
    {},
  );

  const tableData = computed(() =>
    _.sortBy(
      _.flatMap(
        props.ticketDetails.details.config_data.map((item) => {
          const clusterName = clustersMap[item.cluster_id].immute_domain;
          return item.execute_objects.map((executeObject) => ({
            targetCluster: clusterName,
            newDb: executeObject.target_db,
            ips: rulesSetMap[clusterName]?.source_ips ?? [],
          }));
        }),
      ), 'newDb'),
  );

  const columns = computed(() => [
    {
      label: t('目标集群'),
      field: 'targetCluster',
      minWidth: 200,
      width: 250,
      rowspan: ({ row }: { row: RowData }) => {
        const { targetCluster } = row;
        const rowSpan = tableData.value.filter((item) => item.targetCluster === targetCluster).length;
        return rowSpan > 1 ? rowSpan : 1;
      },
    },
    {
      label: t('新DB'),
      field: 'newDb',
      minWidth: 150,
      width: 200,
    },
    {
      label: t('授权的IP'),
      field: 'ips',
      render: ({ data }: { data: RowData }) => (
        <span>
          { data.ips.length > 0 ? data.ips.join(',') : '--' }
          <db-icon
            is-show={data.ips.length > 0}
            class="copy-btn"
            type="copy"
            onClick={() => copy(data.ips.join(','))} />
        </span>
      ),
    },
  ]);
</script>

<style lang="less" scoped>
  .target-cluster-table {
    :deep(.cell) {
      .copy-btn {
        display: none;
        margin-left: 4px;
        color: @primary-color;
        cursor: pointer;
      }
    }

    :deep(tr:hover) {
      .copy-btn[is-show='true'] {
        display: inline-block !important;
      }
    }
  }
</style>
