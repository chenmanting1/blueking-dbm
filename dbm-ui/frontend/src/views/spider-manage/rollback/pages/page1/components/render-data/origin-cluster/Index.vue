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
  <div class="render-data">
    <RenderTable>
      <RenderTableHeadColumn
        :min-width="270"
        :width="280">
        {{ t('待回档集群') }}
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
        :width="120">
        <template #append>
          <BatchEditColumn
            v-model="isShowBatchEdit.backupSource"
            :data-list="selectList.backupSource"
            :title="t('备份源')"
            @change="(value) => handleBatchEdit('backupSource', value)">
            <span
              v-bk-tooltips="t('批量编辑')"
              class="batch-edit-btn"
              @click="handleShowBatchEdit('backupSource')">
              <DbIcon type="bulk-edit" />
            </span>
          </BatchEditColumn>
        </template>
        {{ t('备份源') }}
      </RenderTableHeadColumn>
      <RenderTableHeadColumn
        :min-width="380"
        :width="400">
        <template #append>
          <BatchEditColumn
            v-model="isShowBatchEdit.mode"
            :title="t('回档类型')"
            @change="handleBatchModeEdit">
            <template #content>
              <div
                class="title-spot edit-title"
                style="font-weight: normal">
                {{ t('回档类型') }} <span class="required" />
              </div>
              <BkSelect
                v-model="checkedModeType"
                :clearable="false"
                filterable
                :list="selectList.mode"
                @change="handleModeType" />
              <div v-if="checkedModeType === BackupTypes.TIME">
                <div
                  class="title-spot edit-title mt-24"
                  style="font-weight: normal">
                  {{ t('时间') }} <span class="required" />
                </div>
                <BkDatePicker
                  :clearable="false"
                  :placeholder="t('如：2019-01-30 12:12:21')"
                  style="width: 361px"
                  type="datetime"
                  :value="datePickerValue"
                  @change="handleDatePickerChange" />
              </div>
              <div v-else>
                <div
                  class="title-spot edit-title mt-24"
                  style="font-weight: normal">
                  {{ t('备份文件 (批量编辑仅支持 “指定时间自动匹配” )') }} <span class="required" />
                </div>
                <BkDatePicker
                  :clearable="false"
                  :placeholder="t('如：2019-01-30 12:12:21')"
                  style="width: 361px"
                  type="datetime"
                  :value="datePickerValue"
                  @change="handleDatePickerChange" />
                <div
                  class="mt-4"
                  :style="{ color: '#979ba5', lineHeight: '20px' }">
                  {{ t('自动匹配指定日期前的最新全库备份') }}
                </div>
              </div>
            </template>
          </BatchEditColumn>
          <span
            v-bk-tooltips="t('批量编辑')"
            class="batch-edit-btn"
            @click="handleShowBatchEdit('mode')">
            <DbIcon type="bulk-edit" />
          </span>
        </template>
        {{ t('回档类型') }}
      </RenderTableHeadColumn>
      <RenderTableHeadColumn
        fixed="right"
        :required="false"
        :width="90">
        {{ t('操作') }}
      </RenderTableHeadColumn>
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

  import { BackupTypes, selectList } from '../../common/const';
  import type { IDataRow } from '../Index.vue';

  interface Emits {
    (e: 'showSelector'): void;
    (e: 'batchEdit', obj: Record<string, any>): void;
  }

  const emits = defineEmits<Emits>();

  const { t } = useI18n();

  const checkedModeType = ref(BackupTypes.BACKUPID);
  const datePickerValue = ref('');
  const isShowBatchEdit = reactive({
    backupSource: false,
    mode: false,
    databases: false,
    databasesIgnore: false,
    tables: false,
    tablesIgnore: false,
  });

  const handleModeType = (value: BackupTypes) => {
    checkedModeType.value = value;
  };
  const handleDatePickerChange = (date: string) => {
    datePickerValue.value = date;
  };
  const handleBatchModeEdit = () => {
    if (checkedModeType.value === BackupTypes.TIME) {
      handleBatchEdit('rollbackTime', datePickerValue.value);
      handleBatchEdit('backupid', '');
    } else {
      handleBatchEdit('backupid', datePickerValue.value);
      handleBatchEdit('rollbackTime', '');
    }
  };

  const handleShowBatchEdit = (col: keyof typeof isShowBatchEdit) => {
    isShowBatchEdit[col] = !isShowBatchEdit[col];
  };

  const handleShowBatchSelector = () => {
    emits('showSelector');
  };

  const handleBatchEdit = (key: keyof IDataRow, value: string, isArray = false) => {
    emits('batchEdit', {
      [key]: isArray && value ? value.split('\n') : value,
    });
  };
</script>
<style lang="less">
  .render-data {
    display: block;

    .batch-edit-btn {
      display: inline-block;
      margin-left: 4px;
      line-height: 40px;
      color: #3a84ff;
      vertical-align: top;
      cursor: pointer;
    }
  }
</style>
