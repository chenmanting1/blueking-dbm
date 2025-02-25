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
  <div class="title-spot custom-item-title mt-24">{{ t('轮值起止时间') }}<span class="required" /></div>
  <BkDatePicker
    ref="datePickerRef"
    append-to-body
    :clearable="false"
    :model-value="dateTimeRange"
    style="width: 100%"
    type="daterange"
    @change="handlerChangeDatetime" />
  <div class="title-spot custom-item-title mt-24">{{ t('轮值排班') }}<span class="required" /></div>
  <DbOriginalTable
    class="custom-table-box"
    :columns="columns"
    :data="tableData" />
</template>

<script setup lang="tsx">
  import dayjs from 'dayjs';
  import { useI18n } from 'vue-i18n';
  import { useRequest } from 'vue-request';

  import type { DutyCustomItem } from '@services/model/monitor/duty-rule';
  import DutyRuleModel from '@services/model/monitor/duty-rule';
  import { getUseList } from '@services/source/common';

  import { getDiffDays, random } from '@utils';

  interface Props {
    data?: DutyRuleModel;
    isSetEmpty?: boolean;
  }

  interface RowData {
    dateTime: string,
    timeRange: {
      id: string,
      value: string[];
    }[],
    peoples: string[],
  }

  interface Exposes {
    getValue: () => {
      effective_time: string,
      end_time: string,
      duty_arranges:{
        date: string,
        work_times: string[],
        members: string[],
      }[],
    }
  }

  const props = defineProps<Props>();

  function formatDate(date: string) {
    return dayjs(date).format('YYYY-MM-DD');
  }

  // 临时处理，待时间选择器修复后去除
  function transferToTimePicker(timeStr: string) {
    const arr = timeStr.split(':');
    if (arr.length === 2) {
      return `${timeStr}:00`;
    }
    return timeStr;
  }

  function initDateRange() {
    return [
      formatDate(new Date().toISOString()),
      formatDate(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()),
    ] as [string, string];
  }

  const { t } = useI18n();

  const dateTimeRange = ref<[string, string]>(initDateRange());
  const copiedStr = ref('');
  const tableData = ref<RowData[]>([]);
  const contactList = ref<SelectItem<string>[]>([]);

  const columns = computed(() => ([
    {
      label: t('轮值日期'),
      field: 'dateTime',
      width: 120,
    },
    {
      label: t('轮值时间'),
      field: 'timeRange',
      showOverflowTooltip: true,
      width: 250,
      render: ({ data, index }: {data: RowData, index: number}) => (
        <div class={{ 'time-group-box': true, 'time-group-mutiple': data.timeRange.length > 1 }}>
          {
            data.timeRange.map((item, innerIndex) => (
              <div class="time-item" key={item.id}>
                <bk-time-picker
                  v-model={item.value}
                  clearable={false}
                  type="timerange"
                  append-to-body />
                  {innerIndex === 0 && <db-icon
                    class="ml-10 icon"
                    type="plus-circle"
                    onClick={() => handleAddTime(index)}/>}
                  {innerIndex !== 0 && <db-icon
                    class="ml-10 icon"
                    type="minus-circle"
                    onClick={() => handleDeleteTime(index, innerIndex)}/>}
              </div>
            ))
          }
        </div>
      ),
    },
    {
      label: t('轮值人员'),
      field: 'peoples',
      render: ({ data }: {data: RowData}) => (
        <div class="peoples">
          <bk-select
            class="people-select"
            clearable={false}
            v-model={data.peoples}
            placeholder={t('请选择人员')}
            filterable
            multiple
            input-search={false}
            multiple-mode="tag"
          >
          {
            contactList.value.map((item, index) => <bk-option
              key={index}
              value={item.value}
              label={item.label}
            />)
          }
          </bk-select>
          {/* <bk-tag-input
            clearable={false}
            v-model={data.peoples}
            placeholder={t('请选择人员')}
            allow-create
            has-delete-icon
            collapse-tags
          /> */}
          <div class="operate-box">
            {copiedStr.value !== '' && <db-icon
              class="operate-icon"
              type="paste"
              onClick={() => handleClickPaste(data)}/>}
            {data.peoples.length > 0 && <db-icon
              class="ml-10 operate-icon"
              type="copy-2"
              onClick={() => handleClickCopy(data)}/>}
          </div>
        </div>
        ),
    },
  ]));

  useRequest(getUseList, {
    onSuccess: (res) => {
      const list = res.results.map(item => ({ label: item.username, value: item.username }));
      contactList.value = list;
    },
  });

  watch(dateTimeRange, (range) => {
    const dateArr = getDiffDays(range[0] as string, range[1]);
    tableData.value = dateArr.map(item => ({
      dateTime: item,
      timeRange: [{
        id: random(),
        value: ['00:00:00', '23:59:59'],
      }],
      peoples: [],
    }));
  }, {
    immediate: true,
  });

  watch(() => props.data, (data) => {
    if (data) {
      dateTimeRange.value = [data.effective_time, data.end_time];
      setTimeout(() => {
        const arranges = data.duty_arranges as DutyCustomItem[];
        tableData.value = arranges.map(item => ({
          dateTime: item.date,
          timeRange: item.work_times.map(i => ({
            id: random(),
            value: i.split('--').map(time => transferToTimePicker(time)),
          })),
          peoples: item.members,
        }));
      });
    }
  }, {
    immediate: true,
  });

  watch(() => props.isSetEmpty, (status) => {
    if (status) {
      // 设置初始化
      setTimeout(() => {
        dateTimeRange.value = initDateRange();
      });
    }
  }, {
    immediate: true,
  });

  const handleClickCopy = (row: RowData) => {
    copiedStr.value = row.peoples.join(',');
  };

  const handleClickPaste = (row: RowData) => {
    const oldArr = row.peoples;
    if (oldArr.length === 0) {
      Object.assign(row, {
        peoples: copiedStr.value.split(','),
      });
    } else {
      const addArr = copiedStr.value.split(',');
      const newArr = [...new Set([...oldArr, ...addArr])];
      Object.assign(row, {
        peoples: newArr,
      });
    }
  };

  const handleAddTime = (index: number) => {
    tableData.value[index].timeRange.push({
      id: random(),
      value: ['00:00:00', '23:59:59'],
    });
  };

  const handleDeleteTime = (outerIndex: number, innerIndex: number) => {
    tableData.value[outerIndex].timeRange.splice(innerIndex, 1);
  };

  const handlerChangeDatetime = (range: [string, string]) => {
    dateTimeRange.value = range;
  };

  // 临时处理，待组件支持分钟后去除
  const splitTimeToMinute = (str: string) => {
    const strArr = str.split(':');
    if (strArr.length <= 2) {
      return str;
    }
    strArr.pop();
    return strArr.join(':');
  };

  defineExpose<Exposes>({
    getValue() {
      let effctTime = dateTimeRange.value[0];
      effctTime = `${effctTime.split(' ')[0]} 00:00:00`;
      let endTime = dateTimeRange.value[1];
      endTime = `${endTime.split(' ')[0]} 00:00:00`;
      return {
        effective_time: effctTime,
        end_time: endTime,
        duty_arranges: tableData.value.map(item => ({
          date: item.dateTime,
          work_times: item.timeRange.map(data => data.value.map(str => splitTimeToMinute(str)).join('--')),
          members: item.peoples,
        })),
      };
    },
  });
</script>
<style lang="less" scoped>
  .custom-item-title {
    margin-bottom: 6px;
    font-weight: normal;
    color: #63656e;

    .title-tip {
      margin-left: 6px;
      font-size: 12px;
      color: #979ba5;
    }
  }

  .custom-table-box {
    :deep(td) {
      background-color: #f5f7fa !important;
    }

    :deep(.peoples) {
      position: relative;
      display: flex;
      width: 100%;
      flex-wrap: wrap;

      &:hover {
        .operate-box {
          .operate-icon {
            display: block !important;
          }
        }
      }

      .people-select {
        width: 100%;

        .angle-up {
          display: none !important;
        }
      }

      .bk-tag-input {
        width: 100%;
      }

      .operate-box {
        position: absolute;
        top: 0;
        right: 0;
        z-index: 9999;
        display: flex;
        height: 100%;
        padding-right: 12px;
        align-items: center;

        .operate-icon {
          display: none !important;
          font-size: 16px;
          color: #737987;
          cursor: pointer;
        }
      }
    }

    :deep(.time-group-mutiple) {
      padding: 10px 0;
    }

    :deep(.time-group-box) {
      display: flex;
      width: 100%;
      flex-flow: column wrap;
      gap: 8px;

      .time-item {
        display: flex;
        width: 100%;
        align-items: center;

        .icon {
          font-size: 18px;
          color: #979ba5;
          cursor: pointer;
        }
      }
    }
  }
</style>
