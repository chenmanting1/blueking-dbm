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
  <div
    v-bk-tooltips="{
      disabled: Boolean(clusterData),
      content: t('请先选择集群'),
    }">
    <DisableSelect
      ref="inputRef"
      :data="showText"
      :placeholder="t('请选择')"
      :rules="rules"
      @click="handleShowSelector" />
  </div>
  <DbSideslider
    :before-close="handleClose"
    :is-show="isShowSelector"
    :width="960"
    @closed="handleClose">
    <template #header>
      <span>
        {{ t('选择集群目标方案_n', { n: clusterData?.masterDomain }) }}
        <BkTag theme="info">
          {{ t('存储层 RemoteDB/DR 同时变更') }}
        </BkTag>
      </span>
    </template>
    <div
      v-if="clusterData"
      class="cluster-spec-plan-selector-box">
      <div class="spec-box mb-24">
        <table>
          <tr>
            <td>{{ t('当前规格') }}： {{ clusterData.clusterSpec.spec_name }}</td>
            <td>{{ t('变更后规格') }}： {{ futureSpec.name || '--' }}</td>
          </tr>
          <tr>
            <td>{{ t('当前机器组数') }}： {{ clusterData.machinePairCnt }}</td>
            <td>{{ t('变更机器组数') }}： {{ localSpec?.machine_pair || '--' }}</td>
          </tr>
          <tr>
            <td>
              {{ t('当前容量') }}： <span class="text-bold">{{ clusterData.clusterCapacity }} G</span>
            </td>
            <td>
              {{ t('变更后容量') }}： <span class="text-bold">{{ futureSpec.futureCapacity }} G</span>
            </td>
          </tr>
        </table>
      </div>
      <BkForm label-width="135">
        <ClusterSpecPlanSelector
          v-model:custom-spec-info="customSpecInfo"
          :cloud-id="clusterData.bkCloudId"
          :cluster-shard-num="clusterData.clusterShardNum"
          cluster-type="tendbcluster"
          machine-type="remote"
          @change="handlePlanChange" />
      </BkForm>
    </div>
    <template #footer>
      <BkButton
        class="mr-8"
        theme="primary"
        @click="handleConfirm">
        {{ t('确定') }}
      </BkButton>
      <BkButton @click="handleClose">
        {{ t('取消') }}
      </BkButton>
    </template>
  </DbSideslider>
</template>
<script setup lang="ts">
  import { ref, shallowRef, watch } from 'vue';
  import { useI18n } from 'vue-i18n';

  import { useBeforeClose } from '@hooks';

  import ClusterSpecPlanSelector, { type TicketSpecInfo } from '@components/cluster-spec-plan-selector/Index.vue';
  import DisableSelect from '@components/render-table/columns/select-disable/index.vue';

  import type { IDataRow } from './Row.vue';

  interface Props {
    clusterData?: IDataRow['clusterData'];
  }
  interface Exposes {
    getValue: () => Promise<any>;
  }

  const props = defineProps<Props>();
  defineOptions({
    inheritAttrs: false,
  });

  const { t } = useI18n();
  const handleBeforeClose = useBeforeClose();

  const inputRef = ref();
  const isShowSelector = ref(false);
  const futureSpec = ref({
    name: '',
    futureCapacity: 0,
  });
  const choosedSpecId = ref(-1);

  const localSpec = shallowRef<TicketSpecInfo>();

  const customSpecInfo = reactive({
    specId: '',
    count: 1,
  });

  const showText = computed(() => `${localSpec.value ? `${localSpec.value.cluster_capacity} G` : ''}`);

  const rules = [
    {
      validator: (value: string) => {
        if (value) {
          return true;
        }
        return false;
      },
      message: t('目标总容量不能为空'),
    },
  ];

  watch(
    () => props.clusterData,
    () => {
      if (!props.clusterData) {
        futureSpec.value = {
          name: '',
          futureCapacity: 0,
        };
        localSpec.value = undefined;
      }
    },
  );

  const handleShowSelector = () => {
    if (!props.clusterData) {
      return;
    }
    isShowSelector.value = true;
    choosedSpecId.value = -1;
  };

  const handlePlanChange = (specId: number, specData: TicketSpecInfo) => {
    choosedSpecId.value = specId;
    localSpec.value = specData;
    futureSpec.value = {
      name: specData.spec_name,
      futureCapacity: specData.cluster_capacity,
    };
  };

  const handleConfirm = () => {
    isShowSelector.value = false;
  };

  async function handleClose() {
    const result = await handleBeforeClose(choosedSpecId.value !== -1);
    if (!result) {
      return;
    }
    isShowSelector.value = false;
  }

  defineExpose<Exposes>({
    getValue() {
      return inputRef.value.getValue().then(() => {
        if (!props.clusterData || !localSpec.value) {
          return Promise.reject();
        }
        return {
          remote_shard_num: Math.ceil(props.clusterData.clusterShardNum / localSpec.value.machine_pair),
          resource_spec: {
            backend_group: {
              spec_id: localSpec.value.spec_id,
              count: localSpec.value.machine_pair,
              affinity: '',
            },
          },
        };
      });
    },
  });
</script>
<style lang="less">
  .cluster-spec-plan-selector-box {
    padding: 20px 40px;

    // .bk-form-label {
    //   font-weight: bold;
    // }

    .spec-box {
      width: 100%;
      padding: 16px;
      font-size: 12px;
      line-height: 18px;
      background-color: #fafbfd;

      table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 8px 0;
        table-layout: fixed;
      }

      td {
        height: 18px;

        .text-bold {
          font-weight: bold;
        }
      }
    }
  }
</style>
