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
  <BkSideslider
    v-model:is-show="state.isShow"
    class="log"
    quick-close
    render-directive="if"
    :width="960"
    @hidden="handleClose">
    <template #header>
      <div class="log-header">
        <div class="log-header-left">
          <span
            v-overflow-tips="{
              content: `【${nodeData.name}】 ${t('日志详情')}`,
              theme: 'light',
            }"
            class="log-header__title text-overflow">
            {{ `【${nodeData.name}】 ${t('日志详情')}` }}
          </span>
          <div class="log-header-info">
            <RetrySelector
              :node-id="nodeData.id"
              @change="handleChangeDate" />
            <BkTag
              class="ml-16 mr-16"
              :theme="status.theme">
              {{ status.text }}
            </BkTag>
            <span>
              {{ $t('总耗时') }}
              <CostTimer
                :is-timing="STATUS_RUNNING"
                :start-time="nodeData.started_at"
                :value="costTime" />
            </span>
          </div>
        </div>
        <div
          v-if="STATUS_FAILED && nodeData.retryable"
          class="log-header-btn mr-8">
          <BkPopover
            v-model:is-show="refreshShow"
            theme="light"
            trigger="manual"
            :z-index="99999">
            <BkButton
              class="refresh-btn"
              :loading="retryLoading"
              @click="() => (refreshShow = true)">
              <i class="db-icon-refresh mr5" />{{ $t('失败重试') }}
            </BkButton>
            <template #content>
              <div class="tips-content">
                <div class="title">
                  {{ $t('确定重试吗') }}
                </div>
                <div class="btn">
                  <span
                    class="bk-button-primary bk-button mr-8"
                    @click="handleRefresh">
                    {{ $t('确定') }}
                  </span>
                  <span
                    class="bk-button"
                    @click="() => (refreshShow = false)">
                    {{ $t('取消') }}
                  </span>
                </div>
              </div>
            </template>
          </BkPopover>
        </div>
        <template v-if="failedNodes.length > 0">
          <BkButton
            v-bk-tooltips="t('上一个失败节点')"
            class="quick-btn"
            :disabled="currentFailNodeLogIndex === 0"
            @click="() => handleClickQuickGoto(false)">
            <DbIcon type="up-big" />
          </BkButton>
          <BkButton
            v-bk-tooltips="t('下一个失败节点')"
            class="quick-btn ml-8 mr-16"
            :disabled="currentFailNodeLogIndex === failedNodes.length - 1"
            @click="() => handleClickQuickGoto(true)">
            <DbIcon type="down-big" />
          </BkButton>
        </template>
      </div>
    </template>
    <template #default>
      <div
        ref="logContentRef"
        class="log-content">
        <div class="log-tools">
          <span class="log-tools-title">
            {{ $t('执行日志') }}
            <span> {{ $t('日志保留7天_如需要请下载保存') }}</span>
          </span>
          <div class="log-tools-bar">
            <i
              v-bk-tooltips="$t('复制')"
              class="db-icon-copy"
              @click="handleCopyLog" />
            <i
              v-bk-tooltips="$t('下载')"
              class="db-icon-import"
              @click="handleDownLoaderLog" />
            <i
              v-bk-tooltips="screenIcon.text"
              :class="screenIcon.icon"
              @click="toggle" />
          </div>
        </div>
        <div class="log-details">
          <BkLog ref="logRef" />
        </div>
      </div>
    </template>
  </BkSideslider>
</template>

<script setup lang="tsx">
  import { format } from 'date-fns';
  import { useI18n } from 'vue-i18n';
  import { useRequest } from 'vue-request';

  import { getNodeLog, getRetryNodeHistories, retryTaskflowNode } from '@services/source/taskflow';

  import CostTimer from '@components/cost-timer/CostTimer.vue';
  import BkLog from '@components/vue2/bk-log/index.vue';

  import { messageSuccess } from '@utils';

  import { useFullscreen, useTimeoutPoll } from '@vueuse/core';

  import { NODE_STATUS_TEXT } from '../common/graphRender';
  import type { GraphNode } from '../common/utils';

  import RetrySelector from './RetrySelector.vue';

  import { useCopy } from '@/hooks';

  type NodeLog = ServiceReturnType<typeof getNodeLog>[number];

  interface Props {
    isShow?: boolean;
    node?: GraphNode;
    failedNodes?: GraphNode[];
  }

  interface Emits {
    (e: 'close'): void;
    (e: 'refresh'): void;
    (e: 'quickGoto', index: number, isNext: boolean): void;
  }

  const props = withDefaults(defineProps<Props>(), {
    isShow: false,
    node: () => ({}) as NonNullable<Props['node']>,
    failedNodes: () => [] as NonNullable<Props['failedNodes']>,
  });
  const emits = defineEmits<Emits>();

  const { t } = useI18n();
  const copy = useCopy();
  const route = useRoute();

  const rootId = route.params.root_id as string;

  const refreshShow = ref(false);
  const logRef = ref();
  const logContentRef = ref<HTMLDivElement>();

  const logState = reactive({
    data: [] as NodeLog[],
    loading: false,
  });

  const state = reactive({
    isShow: false,
  });

  const currentFailNodeLogIndex = computed(() =>
    props.failedNodes.findIndex((item) => item.data.id === props.node.data.id),
  );

  const screenIcon = computed(() => ({
    icon: isFullscreen.value ? 'db-icon-un-full-screen' : 'db-icon-full-screen',
    text: isFullscreen.value ? t('取消全屏') : t('全屏'),
  }));

  const nodeData = computed(() => props.node.data || {});
  const status = computed(() => {
    const themesMap = {
      FINISHED: 'success',
      RUNNING: 'info',
      FAILED: 'danger',
      SKIPPED: 'danger',
      READY: '',
      CREATED: '',
    };

    const status = nodeData.value.status ? nodeData.value.status : 'READY';

    return {
      text: NODE_STATUS_TEXT[status],
      theme: themesMap[status],
    };
  });

  const STATUS_RUNNING = computed(() => nodeData.value.status === 'RUNNING');
  const STATUS_FAILED = computed(() => nodeData.value.status === 'FAILED');

  const costTime = computed(() => {
    const { started_at: startedAt, updated_at: updatedAt } = nodeData.value;
    if (startedAt && updatedAt) {
      const time = updatedAt - startedAt;
      return time <= 0 ? 0 : time;
    }
    return 0;
  });

  const { loading: retryLoading, run: runRetryTaskflowNode } = useRequest(retryTaskflowNode, {
    manual: true,
    onSuccess: () => {
      messageSuccess(t('重试成功'));
      location.reload();
    },
  });

  const formatLogData = (data: NodeLog[] = []) => {
    const regex = /^##\[[a-z]+]/;

    return data.map((item) => {
      const { timestamp, message, levelname } = item;
      const time = format(new Date(Number(timestamp)), 'yyyy-MM-dd HH:mm:ss');
      return {
        ...item,
        message: regex.test(message)
          ? message.replace(regex, (match: string) => `${match}[${time} ${levelname}]`)
          : `[${time} ${levelname}] ${message}`,
      };
    });
  };

  /** 获取日志及下载日志接口  */
  const getNodeLogRequest = (isInit?: boolean) => {
    if (!currentData.value.version) {
      return;
    }

    const params = {
      root_id: rootId,
      node_id: nodeData.value.id,
      version_id: currentData.value.version,
    };
    getNodeLog(params)
      .then((res) => {
        logState.data = res;
        handleClearLog();
        handleSetLog(formatLogData(res));
      })
      .finally(() => {
        logState.loading = false;
        isInit && nodeData.value.status === 'RUNNING' && !isActive.value && resume();
      });
  };

  const { isActive, pause, resume } = useTimeoutPoll(getNodeLogRequest, 5000);
  const { isFullscreen, toggle } = useFullscreen(logContentRef);

  watch(
    () => STATUS_RUNNING.value,
    (val) => {
      val && !isActive.value && resume();
      !val && isActive.value && pause();
    },
  );

  watch(
    () => props.isShow,
    () => {
      state.isShow = props.isShow;
    },
    { immediate: true },
  );

  /**
   * 清空日志
   */
  const handleClearLog = () => {
    logRef.value?.handleLogClear();
  };

  /**
   * 设置日志
   */
  const handleSetLog = (data: NodeLog[] = []) => {
    logRef.value.handleLogAdd(data);
  };

  /** 当前选中日志版本的信息 */
  const currentData = ref({ version: '' });
  /**
   * 下载日志
   */
  const handleDownLoaderLog = () => {
    const params: any = {
      root_id: rootId,
      node_id: nodeData.value.id,
      version_id: currentData.value.version,
    };
    const url = `/apis/taskflow/${params.root_id}/node_log/?root_id=${params.root_id}&node_id=${params.node_id}&version_id=${params.version_id}&download=1`;
    const elt = document.createElement('a');
    elt.setAttribute('href', url);
    elt.style.display = 'none';
    document.body.appendChild(elt);
    elt.click();
    document.body.removeChild(elt);
  };
  /**
   * 切换日志版本
   */
  const handleChangeDate = (data: ServiceReturnType<typeof getRetryNodeHistories>[number]) => {
    currentData.value = data;
    pause();
    nextTick(() => {
      logState.loading = true;
      handleClearLog();
      getNodeLogRequest(true);
    });
  };
  const handleCopyLog = () => {
    const logData = formatLogData(logState.data);
    copy(logData.map((item) => item.message).join('\n'));
  };

  const handleRefresh = () => {
    refreshShow.value = false;
    runRetryTaskflowNode({
      root_id: rootId,
      node_id: props.node.id,
    });
  };

  const handleClickQuickGoto = (isNext = false) => {
    emits('quickGoto', currentFailNodeLogIndex.value, isNext);
  };

  /**
   * close slider
   */
  const handleClose = () => {
    emits('close');
    pause();
  };
</script>

<style lang="less" scoped>
  @import '@styles/mixins.less';

  .tips-content {
    font-weight: normal;
    line-height: normal;

    .title {
      padding-bottom: 16px;
      text-align: left;
    }

    .btn {
      margin-top: 0;
    }
  }

  .log {
    .log-header {
      width: 100%;
      .flex-center();

      .log-header-left {
        flex: 1;
        width: 0;
        padding-right: 8px;
        .flex-center();
      }

      .log-header-info {
        padding-left: 4px;
        font-size: @font-size-normal;
        font-weight: normal;
        flex-shrink: 0;
        .flex-center();
      }

      .log-header-btn {
        // padding-right: 13px;
        text-align: right;
        flex-shrink: 0;

        :deep(.bk-button-text) {
          font-size: 14px;
          color: @default-color;

          i {
            display: inline-block;
            margin-right: 5px;
          }
        }
      }

      .quick-btn {
        width: 32px;
        height: 32px;
      }
    }

    :deep(.bk-sideslider-content) {
      height: calc(100vh - 60px);
      padding: 16px;
    }
  }

  .log-content {
    height: 100%;
  }

  .log-tools {
    .flex-center();

    width: 100%;
    height: 42px;
    padding: 0 16px;
    line-height: 42px;
    background: #202024;

    .log-tools-title {
      font-size: 14px;
      color: white;

      span {
        display: inline-block;
        margin-left: 5px;
        color: #c4c6cc;
      }
    }

    .log-tools-bar {
      flex: 1;
      justify-content: flex-end;
      .flex-center();

      i {
        margin-left: 16px;
        font-size: 16px;
        cursor: pointer;
      }
    }
  }

  .log-details {
    height: calc(100% - 42px);
  }
</style>
