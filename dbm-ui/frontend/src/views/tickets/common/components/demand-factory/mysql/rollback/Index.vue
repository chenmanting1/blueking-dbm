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
  <div class="ticket-details__list">
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ t('构造类型') }}：</span>
      <span class="ticket-details__item-value">{{ renderData.label }}</span>
    </div>
  </div>
  <component
    :is="renderData.tableCom"
    class="details-table"
    :ticket-details="ticketDetails" />
</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n';

  import type { MySQLRollbackDetails } from '@services/model/ticket/details/mysql';
  import { RollbackClusterTypes } from '@services/model/ticket/details/mysql';
  import TicketModel from '@services/model/ticket/ticket';

  import RollbackExistCluster from './components/RollbackExistCluster.vue';
  import RollbackNewCluster from './components/RollbackNewCluster.vue';
  import RollbackOriginCluster from './components/RollbackOriginCluster.vue';

  interface Props {
    ticketDetails: TicketModel<MySQLRollbackDetails>;
  }

  const props = defineProps<Props>();

  const { t } = useI18n();

  const rollbackInfo = {
    [RollbackClusterTypes.BUILD_INTO_NEW_CLUSTER]: {
      label: t('构造到新集群'),
      tableCom: RollbackNewCluster,
    },
    [RollbackClusterTypes.BUILD_INTO_EXIST_CLUSTER]: {
      label: t('构造到已有集群'),
      tableCom: RollbackExistCluster,
    },
    [RollbackClusterTypes.BUILD_INTO_METACLUSTER]: {
      label: t('构造到原集群'),
      tableCom: RollbackOriginCluster,
    },
  };

  const renderData = computed(
    () => rollbackInfo[props.ticketDetails.details.rollback_cluster_type as RollbackClusterTypes],
  );
</script>

<style lang="less" scoped>
  @import '@views/tickets/common/styles/DetailsTable.less';
  @import '@views/tickets/common/styles/ticketDetails.less';
</style>
