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
  <BkLoading :loading="isLoading">
    <div
      class="render-cluster-box"
      :class="{ placeholder: !data }">
      <span
        v-if="!data"
        key="empty">
        {{ t('选择主机后自动生成') }}
      </span>
      <template v-else>
        <div
          v-for="item in renderMasters"
          :key="item">
          {{ item }}
        </div>
      </template>
    </div>
  </BkLoading>
</template>
<script setup lang="ts">
  import { useI18n } from 'vue-i18n';

  interface Props {
    data?: string;
    isLoading?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    data: '',
    isLoading: false,
  });

  const { t } = useI18n();

  const renderMasters = computed(() => props.data.split(','));
</script>
<style lang="less" scoped>
  .render-cluster-box {
    padding: 10px 16px;
    line-height: 20px;
    color: #63656e;

    &.placeholder {
      background: #fafbfd;
      color: #c4c6cc;
    }
  }
</style>
