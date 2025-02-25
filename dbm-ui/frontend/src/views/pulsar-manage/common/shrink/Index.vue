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
  <BkLoading
    class="pulsar-cluster-shrink-box"
    :loading="isLoading">
    <BkAlert
      class="mb16"
      theme="warning"
      :title="$t('Bookkeeper_Broker 至少缩容一种类型')" />
    <div class="wrapper">
      <NodeStatusList
        ref="nodeStatusListRef"
        v-model="nodeType"
        :list="nodeStatusList"
        :node-info="nodeInfoMap" />
      <div class="node-panel">
        <HostShrink
          v-if="!isLoading"
          :key="nodeType"
          :data="nodeInfoMap[nodeType]"
          @change="handleNodeHostChange"
          @target-disk-change="handleTargetDiskChange" />
      </div>
    </div>
  </BkLoading>
</template>
<script setup lang="tsx">
  import { InfoBox } from 'bkui-vue';
  import {
    reactive,
    ref,
    watch,
  } from 'vue';
  import { useI18n } from 'vue-i18n';

  import type PulsarModel from '@services/model/pulsar/pulsar';
  import type PulsarNodeModel from '@services/model/pulsar/pulsar-node';
  import { getPulsarNodeList } from '@services/source/pulsar';
  import { createTicket } from '@services/source/ticket';

  import { useTicketMessage } from '@hooks';

  import { useGlobalBizs } from '@stores';

  import HostShrink, {
    type TShrinkNode,
  } from '@components/cluster-common/host-shrink/Index.vue';
  import NodeStatusList from '@components/cluster-common/host-shrink/NodeStatusList.vue';

  import { messageError } from '@utils';

  type TNodeInfo = TShrinkNode<PulsarNodeModel>

  interface Props {
    data: PulsarModel,
    nodeList?: TNodeInfo['nodeList']
  }

  interface Emits {
    (e: 'change'): void
  }

  interface Exposes {
    submit: () => Promise<any>
  }

  const props = withDefaults(defineProps<Props>(), {
    nodeList: () => [],
  });
  const emits = defineEmits<Emits>();

  const { t } = useI18n();
  const globalBizsStore = useGlobalBizs();
  const ticketMessage = useTicketMessage();

  const bizId = globalBizsStore.currentBizId;

  const nodeStatusList = [
    {
      key: 'bookkeeper',
      label: 'Bookkeeper',
    },
    {
      key: 'broker',
      label: 'Broker',
    },
  ];

  const nodeStatusListRef = ref();
  const nodeInfoMap = reactive<Record<string, TNodeInfo>>({
    broker: {
      label: 'Broker',
      originalNodeList: [],
      nodeList: [],
      // 当前主机总容量
      totalDisk: 0,
      // 缩容后的目标容量
      targetDisk: 0,
      // 实际选择的缩容主机容量
      shrinkDisk: 0,
      minHost: 1,
    },
    bookkeeper: {
      label: 'Bookkeeper',
      originalNodeList: [],
      nodeList: [],
      totalDisk: 0,
      targetDisk: 0,
      shrinkDisk: 0,
      minHost: 2,
    },
  });

  const isLoading = ref(false);
  const nodeType = ref('broker');

  const fetchListNode = () => {
    const bookkeeperOriginalNodeList: TNodeInfo['nodeList'] = [];
    const brokerOriginalNodeList: TNodeInfo['nodeList'] = [];

    isLoading.value = true;
    getPulsarNodeList({
      bk_biz_id: globalBizsStore.currentBizId,
      cluster_id: props.data.id,
      no_limit: 1,
    }).then((data) => {
      let bookkeeperDiskTotal = 0;
      let brokerDiskTotal = 0;

      data.results.forEach((nodeItem) => {
        if (nodeItem.isBookkeeper) {
          bookkeeperDiskTotal += nodeItem.disk;
          bookkeeperOriginalNodeList.push(nodeItem);
        } else if (nodeItem.isBroker) {
          brokerDiskTotal += nodeItem.disk;
          brokerOriginalNodeList.push(nodeItem);
        }
      });

      nodeInfoMap.bookkeeper.originalNodeList = bookkeeperOriginalNodeList;
      nodeInfoMap.bookkeeper.totalDisk = bookkeeperDiskTotal;
      if (nodeInfoMap.bookkeeper.shrinkDisk) {
        nodeInfoMap.bookkeeper.targetDisk = bookkeeperDiskTotal - nodeInfoMap.bookkeeper.shrinkDisk;
      }

      nodeInfoMap.broker.originalNodeList = brokerOriginalNodeList;
      nodeInfoMap.broker.totalDisk = brokerDiskTotal;
      if (nodeInfoMap.broker.shrinkDisk) {
        nodeInfoMap.broker.targetDisk = brokerDiskTotal - nodeInfoMap.broker.shrinkDisk;
      }
    })
      .finally(() => {
        isLoading.value = false;
      });
  };

  fetchListNode();

  // 默认选中的缩容节点
  watch(() => props.nodeList, () => {
    const bookkeeperNodeList: TNodeInfo['nodeList'] = [];
    const brokerNodeList: TNodeInfo['nodeList'] = [];

    let bookkeeperShrinkDisk = 0;
    let brokerShrinkDisk = 0;

    props.nodeList.forEach((nodeItem) => {
      if (nodeItem.isBookkeeper) {
        bookkeeperShrinkDisk += nodeItem.disk;
        bookkeeperNodeList.push(nodeItem);
      } else if (nodeItem.isBroker) {
        brokerShrinkDisk += nodeItem.disk;
        brokerNodeList.push(nodeItem);
      }
    });
    nodeInfoMap.bookkeeper.nodeList = bookkeeperNodeList;
    nodeInfoMap.bookkeeper.shrinkDisk = bookkeeperShrinkDisk;
    nodeInfoMap.broker.nodeList = brokerNodeList;
    nodeInfoMap.broker.shrinkDisk = brokerShrinkDisk;
  }, {
    immediate: true,
  });

  // 容量修改
  const handleTargetDiskChange = (value: number) => {
    nodeInfoMap[nodeType.value].targetDisk = value;
  };

  // 缩容节点主机修改
  const handleNodeHostChange = (nodeList: TNodeInfo['nodeList']) => {
    const shrinkDisk = nodeList.reduce((result, hostItem) => result + hostItem.disk, 0);
    nodeInfoMap[nodeType.value].nodeList = nodeList;
    nodeInfoMap[nodeType.value].shrinkDisk = shrinkDisk;
  };

  defineExpose<Exposes>({
    submit() {
      return new Promise((resolve, reject) => {
        if (!nodeStatusListRef.value.validate()) {
          messageError(t('Bookkeeper_Broker 至少缩容一种类型'));
          return reject();
        }

        const renderSubTitle = () => {
          const renderDiskTips = () => {
            const isNotMatch = Object.values(nodeInfoMap)
              .some(nodeData => nodeData.totalDisk + nodeData.shrinkDisk !== nodeData.targetDisk);
            if (isNotMatch) {
              return (
                <>
                  <div>{t('目标容量与所选 IP 容量不一致，确认提交？')}</div>
                  <div>{t('继续提交将按照手动选择的 IP 容量进行')}</div>
                </>
              );
            }
            return null;
          };
          const renderShrinkDiskTips = () => Object.values(nodeInfoMap).map((nodeData) => {
            if (nodeData.shrinkDisk) {
              return (
                <div>
                  {t('name容量从nG缩容至nG', {
                    name: nodeData.label,
                    totalDisk: nodeData.totalDisk,
                    targetDisk: nodeData.totalDisk - nodeData.shrinkDisk,
                  })}
                </div>
              );
            }
            return null;
          });

          return (
          <div style="font-size: 14px; line-height: 28px; color: #63656E;">
            {renderDiskTips()}
            {renderShrinkDiskTips()}
          </div>
          );
        };

        InfoBox({
          title: t('确认缩容【name】集群', { name: props.data.cluster_name }),
          subTitle: renderSubTitle,
          confirmText: t('确认'),
          cancelText: t('取消'),
          headerAlign: 'center',
          contentAlign: 'center',
          footerAlign: 'center',
          onCancel: () => reject(),
          onConfirm: () => {
            const fomatHost = (nodeList: TNodeInfo['nodeList'] = []) => nodeList.map(hostItem => ({
              ip: hostItem.ip,
              bk_cloud_id: hostItem.bk_cloud_id,
              bk_host_id: hostItem.bk_host_id,
              bk_biz_id: bizId,
            }));

            const generateExtInfo = () => Object.entries(nodeInfoMap).reduce((results, [key, item]) => {
              const obj = {
                host_list: item.nodeList.map(item => ({
                  ip: item.ip,
                  bk_disk: item.disk,
                  alive: item.status,
                })),
                total_hosts: item.originalNodeList.length,
                total_disk: item.totalDisk,
                target_disk: item.targetDisk,
                shrink_disk: item.shrinkDisk,
              };
              Object.assign(results, {
                [key]: obj,
              });
              return results;
            }, {} as Record<string, any>);

            createTicket({
              ticket_type: 'PULSAR_SHRINK',
              bk_biz_id: bizId,
              details: {
                cluster_id: props.data.id,
                ip_source: 'manual_input',
                nodes: {
                  broker: fomatHost(nodeInfoMap.broker.nodeList),
                  bookkeeper: fomatHost(nodeInfoMap.bookkeeper.nodeList),
                },
                ext_info: generateExtInfo(),
              },
            }).then((data) => {
              ticketMessage(data.id);
              resolve('success');
              emits('change');
            })
          },
        });
      });
    },
  });
</script>
<style lang="less">
  .pulsar-cluster-shrink-box {
    padding: 18px 43px 18px 37px;
    font-size: 12px;
    line-height: 20px;
    color: #63656e;
    background: #f5f7fa;

    .wrapper {
      display: flex;
      background: #fff;
      border-radius: 2px;
      box-shadow: 0 2px 4px 0 #1919290d;

      .node-panel {
        flex: 1;
      }
    }

    .item-label {
      margin-top: 24px;
      margin-bottom: 6px;
      font-weight: bold;
      line-height: 20px;
      color: #313238;
    }
  }
</style>
