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
  <BkLoading :loading="loading">
    <div
      ref="textRef"
      class="render-text-box"
      :class="{
        'default-display': showDefault,
      }">
      <span
        v-if="showDefault"
        style="color: #c4c6cc">
        {{ t('输入集群后自动生成') }}
      </span>
      <template v-else>
        <BkOverflowTitle
          v-for="name in currentVersionList"
          :key="name"
          v-overflow-title>
          {{ name }}
        </BkOverflowTitle>
      </template>
    </div>
  </BkLoading>
</template>
<script setup lang="ts">
  import { useI18n } from 'vue-i18n';
  import { useRequest } from 'vue-request';

  import { getClusterVersions } from '@services/source/redisToolbox';

  import type { IDataRow } from './Row.vue';

  interface Props {
    data: IDataRow;
  }

  interface Emits {
    (e: 'list-change', value: string[]): void;
  }

  const props = defineProps<Props>();

  const emits = defineEmits<Emits>();

  const { t } = useI18n();

  const currentVersionList = ref<string[]>([]);

  const showDefault = computed(() => currentVersionList.value.length === 0);

  const { loading, run: fetchCurrentClusterVersions } = useRequest(getClusterVersions, {
    manual: true,
    onSuccess(versions) {
      currentVersionList.value = versions;
      emits('list-change', versions);
    },
  });

  watch(
    () => [props.data.clusterId, props.data.nodeType],
    () => {
      if (props.data.clusterId) {
        fetchCurrentClusterVersions({
          node_type: props.data.nodeType,
          type: 'online',
          cluster_id: props.data.clusterId,
        });
      }
    },
    {
      immediate: true,
    },
  );
</script>
<style lang="less" scoped>
  .render-text-box {
    position: relative;
    width: 100%;
    min-height: 42px;
    padding: 10px 16px;
    overflow: hidden;
    line-height: 20px;
    color: #63656e;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .default-display {
    cursor: not-allowed;
    background: #fafbfd;
  }
</style>
