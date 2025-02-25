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
  <div class="cluster-node-list-box">
    <div style="margin-bottom: 12px">
      <BkButton
        :disabled="isBatchRestartDisabled || isRestartActionDisabled"
        :loading="isBatchRestartLoading"
        @click="handleBatchRestart">
        {{ $t('批量重启') }}
      </BkButton>
    </div>
    <BkLoading
      :loading="isLoading"
      :z-index="2">
      <DbOriginalTable
        :columns="columns"
        :data="tableData"
        :is-anomalies="isAnomalies"
        @refresh="fetchData(true)"
        @select="handleSelect"
        @select-all="handleSelectAll" />
    </BkLoading>
  </div>
</template>
<script setup lang="tsx">
  import { InfoBox } from 'bkui-vue';
  import {
    ref,
    shallowRef,
  } from 'vue';
  import { useI18n } from 'vue-i18n';

  import type PulsarInstanceModel from '@services/model/pulsar/pulsar-instance';
  import type PulsarNodeModel from '@services/model/pulsar/pulsar-node';
  import { getPulsarInstanceList } from '@services/source/pulsar';
  import { createTicket } from '@services/source/ticket';

  import { useTicketMessage } from '@hooks';

  import { useGlobalBizs } from '@stores';

  import OperationBtnStatusTips from '@components/cluster-common/OperationBtnStatusTips.vue';
  import RenderInstanceStatus from '@components/cluster-common/RenderInstanceStatus.vue';
  import RenderOperationTag from '@components/cluster-common/RenderOperationTag.vue';

  import { useTimeoutPoll } from '@vueuse/core';

  interface Props {
    clusterId: number,
    data: PulsarNodeModel
  }

  const props = defineProps<Props>();
  const { t } = useI18n();
  const ticketMessage = useTicketMessage();

  const formatRequestData = (data: Array<PulsarInstanceModel>) => data.map((item) => {
    const [ip, port] = item.instance_address.split(':');
    return ({
      ip,
      port: Number(port),
      instance_name: item.instance_name,
      bk_host_id: item.bk_host_id,
      bk_cloud_id: item.bk_cloud_id,
      instance_id: item.id,
    });
  });

  const isAnomalies = ref(false);
  const isLoading = ref(true);
  const isBatchRestartLoading = ref(false);
  const isRestartLoading = ref(false);
  const isRestartActionDisabled = ref(false);
  const tableData = shallowRef<Array<PulsarInstanceModel>>([]);
  const batchSelectNodeMap = shallowRef<Record<number, PulsarInstanceModel>>({});

  const globalBizsStore = useGlobalBizs();

  const isBatchRestartDisabled = computed(() => Object.keys(batchSelectNodeMap.value).length < 1);

  const columns = [
    {
      type: 'selection',
      width: 48,
      label: '',
      fixed: 'left',
    },
    {
      label: t('实例'),
      field: 'instance_address',
      showOverflowTooltip: false,
      render: ({ data }: {data:PulsarInstanceModel}) => (
        <div style="display: flex; align-items: center;">
          <span class="text-overflow mr4" v-overflow-tips>
            {data.instance_address || '--'}
          </span>
          {
            data.operationTagTips.map(item => <RenderOperationTag class="instance-tag ml-4" data={item}/>)
          }
        </div>
      ),
    },
    {
      label: t('实例状态'),
      field: 'status',
      render: ({ data }: {data: PulsarInstanceModel}) => (
        <>
          {data.operationRunningStatus
            ? (
              <div class='loading-box'>
                <db-icon
                  class="rotate-loading"
                  style="margin-right: 4px"
                  type='loading'
                  svg />
                <div>{ t('重启中') }</div>
              </div>
            )
            : <RenderInstanceStatus data={data.status} />
          }
        </>
      ),
    },
    {
      label: t('上次重启时间'),
      render: ({ data }: {data:PulsarInstanceModel}) => data.restart_at || '--',
    },
    {
      label: t('操作'),
      width: 116,
      render: ({ data }: {data:PulsarInstanceModel}) => (
        <OperationBtnStatusTips data={data}>
          <bk-button
            theme="primary"
            text
            disabled={data.operationDisabled || isRestartActionDisabled.value}
            onClick={() => handleRestartOnde(data)}>
            { t('重启') }
          </bk-button>
        </OperationBtnStatusTips>
      ),
    },
  ];

  const fetchData = (hasLoading = false) => {
    isLoading.value = hasLoading;
    getPulsarInstanceList({
      bk_biz_id: globalBizsStore.currentBizId,
      cluster_id: props.clusterId,
      ip: props.data.ip,
    }).then((data) => {
      tableData.value = data.results;
      isAnomalies.value = false;
    })
      .catch(() => {
        tableData.value = [];
        isAnomalies.value = true;
      })
      .finally(() => {
        isLoading.value = false;
      });
  };

  useTimeoutPoll(fetchData, 5000, {
    immediate: true,
  });

  // 选择单台
  const handleSelect = (data: { checked: boolean, row: PulsarInstanceModel }) => {
    const selectedMap = { ...batchSelectNodeMap.value };
    if (data.checked) {
      selectedMap[data.row.id] = data.row;
    } else {
      delete selectedMap[data.row.id];
    }

    batchSelectNodeMap.value = selectedMap;
  };

  // 选择所有
  const handleSelectAll = (data:{checked: boolean}) => {
    let selectedMap = { ...batchSelectNodeMap.value };
    if (data.checked) {
      selectedMap = tableData.value.reduce((result, item) => ({
        ...result,
        [item.id]: item,
      }), {});
    } else {
      selectedMap = {};
    }
    batchSelectNodeMap.value = selectedMap;
  };

  // 批量重试
  const handleBatchRestart = () => {
    isBatchRestartLoading.value = true;
    InfoBox({
      title: t('确认批量重启'),
      subTitle: '',
      confirmText: t('确认'),
      cancelText: t('取消'),
      headerAlign: 'center',
      contentAlign: 'center',
      footerAlign: 'center',
      onClose: () => {
        isBatchRestartLoading.value = false;
      },
      onConfirm: () => {
        isRestartActionDisabled.value = true;
        createTicket({
          bk_biz_id: globalBizsStore.currentBizId,
          ticket_type: 'PULSAR_REBOOT',
          details: {
            cluster_id: props.clusterId,
            instance_list: formatRequestData(Object.values(batchSelectNodeMap.value)),
          },
        })
          .then((res) => {
            ticketMessage(res.id);
            fetchData();
          })
          .finally(() => {
            isRestartActionDisabled.value = false;
            isBatchRestartLoading.value = false;
          });
      },
    });
  };

  // 重试单台
  const handleRestartOnde = (data: PulsarInstanceModel) => {
    isRestartLoading.value = true;
    InfoBox({
      title: t('确认重启该实例？'),
      subTitle: () => (
        <div>
          <div>{data.instance_address}</div>
          <div class="mt-12">{t('连接将会断开，请谨慎操作！')}</div>
        </div>
      ),
      confirmText: t('确认重启'),
      cancelText: t('取消'),
      headerAlign: 'center',
      contentAlign: 'center',
      footerAlign: 'center',
      onCancel: () => {
        isRestartLoading.value = false;
      },
      onConfirm: () => {
        isRestartActionDisabled.value = true;
        createTicket({
          bk_biz_id: globalBizsStore.currentBizId,
          ticket_type: 'PULSAR_REBOOT',
          details: {
            cluster_id: props.clusterId,
            instance_list: formatRequestData([data]),
          },
        })
          .then((res) => {
            ticketMessage(res.id);
            fetchData();
          })
          .finally(() => {
            isRestartActionDisabled.value = false;
            isRestartLoading.value = false;
          });
      },
    });
  };
</script>
<style lang="less">
  .cluster-node-list-box {
    padding: 28px 40px;

    .loading-box {
      display: flex;
      align-items: center;
    }

    .instance-tag {
      margin-left: 3px;
      flex-shrink: 0;

      span {
        display: block;
        width: 38px;
        height: 16px;
      }

      svg {
        vertical-align: top;
      }
    }
  }
</style>
