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
  <div class="db-table-backup-render-data">
    <RenderTable>
      <template #default>
        <RenderTableHeadColumn
          :min-width="110"
          :width="190">
          {{ t('目标集群') }}
          <template #append>
            <span
              class="batch-edit-btn"
              @click="handleShowBatchSelector">
              <DbIcon type="batch-host-select" />
            </span>
          </template>
        </RenderTableHeadColumn>
        <RenderTableHeadColumn
          :min-width="100"
          :width="170">
          <template #append>
            <BatchEditColumn
              v-model="isShowBatchEdit"
              :data-list="selectList"
              :title="t('备份位置')"
              @change="handleBatchEdit">
              <span
                v-bk-tooltips="t('批量编辑')"
                class="batch-edit-btn"
                @click="handleShowBatchEdit">
                <DbIcon type="bulk-edit" />
              </span>
            </BatchEditColumn>
          </template>
          {{ t('备份位置') }}
        </RenderTableHeadColumn>
        <RenderTableHeadColumn
          :min-width="90"
          :width="210">
          {{ t('备份DB名') }}
        </RenderTableHeadColumn>
        <RenderTableHeadColumn
          :min-width="90"
          :width="210">
          {{ t('备份表名') }}
        </RenderTableHeadColumn>
        <RenderTableHeadColumn
          :min-width="90"
          :required="false"
          :width="210">
          {{ t('忽略DB名') }}
        </RenderTableHeadColumn>
        <RenderTableHeadColumn
          :min-width="90"
          :required="false"
          :width="210">
          {{ t('忽略表名') }}
        </RenderTableHeadColumn>
        <RenderTableHeadColumn
          fixed="right"
          :required="false"
          :width="100">
          {{ t('操作') }}
        </RenderTableHeadColumn>
      </template>

      <template #data>
        <slot />
      </template>
    </RenderTable>
  </div>
</template>
<script setup lang="ts">
  import { useI18n } from 'vue-i18n';

  import BatchEditColumn from '@components/batch-edit-column/Index.vue';
  import RenderTableHeadColumn from '@components/render-table/HeadColumn.vue';
  import RenderTable from '@components/render-table/Index.vue';

  interface Emits{
    (e: 'batchSelectCluster'): void,
    (e: 'batchEditBackupLocal', value: string): void,
  }

  const emits = defineEmits<Emits>();

  const { t } = useI18n();

  const isShowBatchEdit = ref(false);

  const selectList = [
    {
      value: 'remote',
      label: 'remote',
    },
  ];

  const handleShowBatchSelector = () => {
    emits('batchSelectCluster');
  };

  const handleShowBatchEdit = () => {
    isShowBatchEdit.value = !isShowBatchEdit.value;
  };

  const handleBatchEdit = (value: string) => {
    emits('batchEditBackupLocal', value);
  };
</script>
<style lang="less">
  .db-table-backup-render-data {
    .batch-edit-btn {
      margin-left: 4px;
      color: #3a84ff;
      cursor: pointer;
    }
  }
</style>
