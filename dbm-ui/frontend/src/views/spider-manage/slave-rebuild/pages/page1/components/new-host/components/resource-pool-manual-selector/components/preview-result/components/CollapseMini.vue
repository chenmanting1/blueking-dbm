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
    class="collapse-mini"
    :class="[{ 'collapse-mini-collapse': localCollapse }]">
    <div
      class="collapse-mini-header"
      @click="handleToggle">
      <DbIcon class="collapse-mini-icon" type="down-big" />
      <slot name="title">
        <p>
          <span>【{{ title }}】</span>
          -
        </p>
        <I18nT
          keypath="共n条"
          tag="span">
          <template #n>
            <strong style="color: #3a84ff">{{ count }}</strong>
          </template>
        </I18nT>
      </slot>
    </div>

    <Transition mode="in-out">
      <div v-show="localCollapse">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
  interface Props {
    collapse: boolean;
    title: string;
    count: number;
  }

  const props = defineProps<Props>();

  const localCollapse = ref(props.collapse)

  watch(
    () => props.collapse,
    () => {
      localCollapse.value = props.collapse;
    },
  );

  const handleToggle = () => {
    localCollapse.value = !localCollapse.value;
  }
</script>

<style lang="less" scoped>
  @import '@styles/mixins.less';

  .collapse-mini {
    margin-top: 16px;

    &:first-child {
      margin-top: 0;
    }

    .collapse-mini-header {
      height: 24px;
      padding-bottom: 4px;
      cursor: pointer;
      .flex-center();
    }

    .collapse-mini-icon {
      font-size: @font-size-normal;
      transform: rotate(-90deg);
      transition: all 0.2s;
    }

    .collapse-mini-collapse {
      .collapse-mini-icon {
        transform: rotate(0);
      }
    }
  }
</style>
