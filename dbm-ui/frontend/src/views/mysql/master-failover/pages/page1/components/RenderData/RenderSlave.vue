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
  <div class="render-slave-box">
    <TableEditSelect
      ref="editRef"
      v-model="localValue"
      :list="slaveHostSelectList"
      :placeholder="t('请输入选择从库')"
      :rules="rules" />
  </div>
</template>
<script lang="ts">
  const singleHostSelectMemo: { [key: string]: Record<string, boolean> } = {};
</script>
<script setup lang="ts">
  import _ from 'lodash';
  import { ref, shallowRef, watch } from 'vue';
  import { useI18n } from 'vue-i18n';

  import { getIntersectedSlaveMachinesFromClusters } from '@services/source/mysqlCluster';

  import { useGlobalBizs } from '@stores';

  import TableEditSelect from '@components/render-table/columns/select/index.vue';

  import { random } from '@utils';

  import type { IDataRow } from './Row.vue';

  interface Props {
    modelValue: IDataRow['slaveData'];
    clusterList: number[];
  }

  interface Exposes {
    getValue: (field: string) => Promise<string>;
  }

  interface ISlaveHost {
    bk_biz_id: number;
    bk_cloud_id: number;
    bk_host_id: number;
    ip: string;
  }

  const props = defineProps<Props>();

  const genHostKey = (hostData: any) => `${hostData.ip}`;

  const instanceKey = `render_slave_${random()}`;
  singleHostSelectMemo[instanceKey] = {};

  const { currentBizId } = useGlobalBizs();
  const { t } = useI18n();

  const editRef = ref();
  const localValue = ref('');
  const slaveHostSelectList = shallowRef([] as Array<{ value: string; label: string }>);
  let allSlaveHostList: ISlaveHost[] = [];

  const rules = [
    {
      validator: (value: string) => !!_.find(allSlaveHostList, (item) => genHostKey(item) === value),
      message: t('目标从库不能为空'),
    },
  ];

  watch(
    () => props.modelValue,
    () => {
      if (props.modelValue) {
        localValue.value = props.modelValue.ip;
      }
    },
    {
      immediate: true,
    },
  );

  watch(
    () => props.clusterList,
    () => {
      localValue.value = '';
      slaveHostSelectList.value = [];
      allSlaveHostList = [];

      if (props.clusterList.length > 0) {
        getIntersectedSlaveMachinesFromClusters({
          bk_biz_id: currentBizId,
          cluster_ids: props.clusterList,
        }).then((data) => {
          slaveHostSelectList.value = data.map((hostData) => ({
            value: genHostKey(hostData),
            label: hostData.ip,
          }));
          allSlaveHostList = data;
        });
      }
    },
    {
      immediate: true,
    },
  );

  defineExpose<Exposes>({
    getValue() {
      return editRef.value.getValue().then(() => {
        const slaveHostData = _.find(allSlaveHostList, (item) => genHostKey(item) === localValue.value);
        return {
          slave_ip: slaveHostData,
        };
      });
    },
  });
</script>
<style lang="less" scoped>
  .render-slave-box {
    position: relative;
  }
</style>
