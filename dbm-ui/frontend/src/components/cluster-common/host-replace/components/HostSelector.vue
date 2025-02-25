<template>
  <div class="replace-host-selector">
    <div
      v-show="data.hostList.length > 0"
      class="selector-value">
      <div>
        <div
          v-for="hostItem in data.hostList"
          :key="hostItem.host_id"
          class="data-row">
          <div>{{ hostItem.ip }}</div>
          <div
            class="data-row-remve-btn"
            @click="handleRemoveHost(hostItem)">
            <DbIcon type="close" />
          </div>
        </div>
      </div>
    </div>
    <div
      v-show="data.hostList.length < 1"
      class="selector-box">
      <IpSelector
        v-model:show-dialog="isShowIpSelector"
        :biz-id="currentBizId"
        :cloud-info="cloudInfo"
        :disable-dialog-submit-method="disableDialogSubmitMethod"
        :disable-host-method="disableHostMethod"
        :os-types="[OSTypes.Linux]"
        :show-view="false"
        @change="handleHostChange">
        <template #submitTips="{ hostList: resultHostList }">
          <I18nT
            keypath="需n台_已选n台"
            style="font-size: 14px; color: #63656e"
            tag="span">
            <span
              class="number"
              style="color: #2dcb56">
              {{ data.nodeList.length }}
            </span>
            <span
              class="number"
              style="color: #3a84ff">
              {{ resultHostList.length }}
            </span>
          </I18nT>
        </template>
      </IpSelector>
    </div>
    <Teleport :to="`#${placehoderId}`">
      <span
        v-if="data.hostList.length > 0"
        class="ip-edit-btn"
        @click="handleShowIpSelector">
        <DbIcon type="edit" />
      </span>
    </Teleport>
  </div>
</template>
<script
  setup
  lang="ts"
  generic="T extends EsNodeModel | HdfsNodeModel | KafkaNodeModel | PulsarNodeModel | InfluxdbInstanceModel">
  import { ref } from 'vue';
  import { useI18n } from 'vue-i18n';

  import type EsNodeModel from '@services/model/es/es-node';
  import type HdfsNodeModel from '@services/model/hdfs/hdfs-node';
  import type InfluxdbInstanceModel from '@services/model/influxdb/influxdbInstance';
  import type KafkaNodeModel from '@services/model/kafka/kafka-node';
  import type PulsarNodeModel from '@services/model/pulsar/pulsar-node';

  import { useGlobalBizs } from '@stores';

  import { OSTypes } from '@common/const';

  import IpSelector from '@components/ip-selector/IpSelector.vue';

  import type { TReplaceNode } from '../Index.vue';

  interface Props {
    data: TReplaceNode<T>;
    placehoderId: string;
    disableHostMethod?: (params: Props['data']['hostList'][0]) => string | boolean;
  }

  const props = defineProps<Props>();
  const modelValue = defineModel<Props['data']['hostList']>({
    required: true,
  });

  const { currentBizId } = useGlobalBizs();
  const { t } = useI18n();

  const cloudInfo = computed(() => {
    const [firstItem] = props.data.nodeList;
    if (firstItem) {
      return {
        id: firstItem.bk_cloud_id,
        name: firstItem.bk_cloud_name,
      };
    }
    return undefined;
  });

  const disableDialogSubmitMethod = (hostList: Props['data']['hostList']) =>
    hostList.length === props.data.nodeList.length ? false : t('需n台', { n: props.data.nodeList.length });

  const isShowIpSelector = ref(false);

  // 添加新IP
  const handleHostChange = (hostList: Props['data']['hostList']) => {
    modelValue.value = hostList;
  };

  // 移除替换的主机
  const handleRemoveHost = (host: Props['data']['hostList'][0]) => {
    modelValue.value = modelValue.value.reduce(
      (result, item) => {
        if (item.host_id !== host.host_id) {
          result.push(item);
        }
        return result;
      },
      [] as Props['data']['hostList'],
    );
  };

  const handleShowIpSelector = () => {
    isShowIpSelector.value = true;
  };
</script>
<style lang="less" scoped>
  .replace-host-selector {
    font-size: 12px;
    color: #63656e;

    .selector-value {
      height: 100%;

      .data-row {
        display: flex;
        height: 42px;
        align-items: center;
        padding-left: 16px;

        & ~ .data-row {
          border-top: 1px solid #dcdee5;
        }

        &:hover {
          .data-row-remve-btn {
            opacity: 100%;
          }
        }
      }

      .data-row-remve-btn {
        display: flex;
        width: 52px;
        height: 100%;
        margin-left: auto;
        font-size: 16px;
        color: #3a84ff;
        cursor: pointer;
        opacity: 0%;
        transition: all 0.15s;
        justify-content: center;
        align-items: center;
      }
    }

    .selector-box {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }
  }
</style>
