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
  <td
    :class="{ 'toolbox-right-fixed-column': isFixedRight, 'toolbox-left-fixed-column': isFixedLeft }"
    style="padding: 0">
    <slot />
  </td>
</template>
<script setup lang="ts">
  import { renderTablekey } from '@components/render-table/Index.vue';

  interface Props {
    fixed?: 'right' | 'left';
  }

  const props = withDefaults(defineProps<Props>(), {
    fixed: 'right',
  });

  const { isOverflow: isFixed, isScrollToLeft, isScrollToRight } = inject(renderTablekey)!;

  const isFixedRight = computed(() => isFixed?.value && props.fixed === 'right' && !isScrollToRight.value);
  const isFixedLeft = computed(() => isFixed?.value && props.fixed === 'left' && !isScrollToLeft.value);
</script>
