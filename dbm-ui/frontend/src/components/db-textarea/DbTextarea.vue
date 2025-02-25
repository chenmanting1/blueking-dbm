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
    ref="dbTextareaRef"
    class="db-textarea"
    :style="{ height: displayHeightValue }">
    <div
      v-if="teleportToBody && state.isTeleport === false"
      class="db-textarea-display"
      :style="{ 'line-height': displayHeightValue }"
      @click.stop="handleEdit">
      <div
        v-overflow-tips
        class="db-textarea-values text-overflow">
        {{ renderValues }}
      </div>
      <span class="db-textarea-placeholder">{{ placeholder }}</span>
    </div>
    <Teleport
      :disabled="!state.isTeleport"
      to="body">
      <BkInput
        v-show="teleportToBody === false || state.isTeleport"
        ref="textareaRef"
        v-bind="$attrs"
        v-model="modelValue"
        :style="style"
        type="textarea"
        @blur="handleBlur"
        @change="handleChange"
        @clear="() => emits('clear')"
        @focus="handleFocus"
        @input="handleInput"
        @paste="handlePaste" />
    </Teleport>
  </div>
</template>

<script lang="ts">
  export default {
    name: 'DbTextarea',
    inheritAttrs: false,
  };
</script>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n';

  import { encodeMult } from '@utils';

  interface Props {
    displayHeight?: number | string
    maxHeight?: number,
    teleportToBody?: boolean,
    rowHeight?: number,
  }

  interface Emits {
    (e: 'focus', value: FocusEvent): void
    (e: 'blur', value: FocusEvent): void
    (e: 'change', value: string): void
    (e: 'input', value: string): void
    (e: 'clear'): void
  }

  const props = withDefaults(defineProps<Props>(), {
    displayHeight: 'auto',
    maxHeight: 70,
    teleportToBody: true,
    rowHeight: 18,
  });
  const emits = defineEmits<Emits>();
  const modelValue = defineModel<string>({
    default: '',
  });

  const attrs = useAttrs();
  const { t } = useI18n();

  const state = reactive({
    isTeleport: false,
  });
  const inputPosition = reactive({
    width: 0,
    x: 0,
    y: 0,
  });
  const textareaRef = ref();
  const dbTextareaRef = ref<HTMLDivElement>();
  // const rowHeight = 18;
  const textareaPadding = 12;
  const rows = ref(1);
  // const height = computed(() => rows.value * rowHeight);
  // bk textarea style
  const style = computed(() => Object.assign({ maxHeight: `${props.maxHeight}px`, '--row-height': `${props.rowHeight}px` }, attrs.style || {}));
  const renderValues = computed(() => modelValue.value.split('\n').join(', '));
  const placeholder = computed(() => {
    if (renderValues.value) return '';

    return (attrs.placeholder || t('请输入')) as string;
  });
  const displayHeightValue = computed(() => (typeof props.displayHeight === 'string' ? props.displayHeight : `${props.displayHeight}px`));

  // 初始化 rows
  if (typeof props.displayHeight === 'number') {
    rows.value = Math.max((props.displayHeight - textareaPadding) / props.rowHeight, 1);
  }

  onMounted(() => {
    setTextareaHeight();
  });

  const handleEdit = () => {
    // 为了解决第一次用 getBoundingClientRect 获取信息不准确问题
    if (dbTextareaRef.value) {
      const {
        x,
        y,
        width,
      } = dbTextareaRef.value.getBoundingClientRect();
      inputPosition.x = x;
      inputPosition.y = y;
      inputPosition.width = width;
    }

    state.isTeleport = true;
    nextTick(() => {
      focus();
    });
  };

  const setTextareaHeight = () => {
    const nums = modelValue.value.split('\n').length;
    rows.value = Math.max(nums, 1);

    if (textareaRef.value?.$el) {
      const el = textareaRef.value.$el as HTMLDivElement;
      const minHeight = typeof props.displayHeight === 'number' ? Math.max(props.displayHeight, props.rowHeight) : props.rowHeight;
      const height = Math.max(rows.value * props.rowHeight + textareaPadding, minHeight);
      el.style.height = `${height}px`;
    }
  };

  const handleFocus = (e: FocusEvent) => {
    const { sourceCapabilities } = e; // 通过该属性判断是否由用户触发
    sourceCapabilities && emits('focus', e);

    if (dbTextareaRef.value && props.teleportToBody) {
      const el = textareaRef.value.$el as HTMLDivElement;
      const { x, y, width } = dbTextareaRef.value.getBoundingClientRect();
      el.style.transition = 'unset';
      el.style.width = `${inputPosition.width || width}px`;
      el.style.position = 'fixed';
      el.style.top = `${inputPosition.y || y}px`;
      el.style.left = `${inputPosition.x || x}px`;
      el.style.zIndex = '99999';
      state.isTeleport = true;

      nextTick(() => {
        // 移动 dom 后会失去焦点，需要重新聚焦
        if (sourceCapabilities) {
          textareaRef.value?.focus();
        }
      });
    }
  };

  const handleBlur = (e: FocusEvent) => {
    const { sourceCapabilities } = e; // 通过该属性判断是否由用户触发
    sourceCapabilities && emits('blur', e);

    if (textareaRef.value?.$el && sourceCapabilities && props.teleportToBody) {
      const el = textareaRef.value.$el as HTMLDivElement;
      el.style.width = '';
      el.style.position = '';
      el.style.top = '';
      el.style.left = '';
      el.style.zIndex = '';
      state.isTeleport = false;
    }

    inputPosition.x = 0;
    inputPosition.y = 0;
    inputPosition.width = 0;
  };

  const handleInput = (value: string) => {
    setTextareaHeight();
    emits('input', value);
    modelValue.value = value;
  };

  const handleChange = (value: string) => {
    emits('change', value);
    modelValue.value = value;
  };

  /**
   * textarea get focus
   */
  const focus = () => {
    textareaRef.value?.focus?.();
  };

  const handlePaste = (value: string, event: ClipboardEvent) => {
    event.preventDefault();
    let paste = (event.clipboardData || window.clipboardData).getData('text');
    paste = encodeMult(paste);
    modelValue.value = paste.replace(/^\s+|\s+$/g, '');
  };

  defineExpose({
    setTextareaHeight,
    focus,
  });
</script>

<style lang="less" scoped>
  .db-textarea {
    min-height: 32px;
    font-size: 0;

    &-display {
      position: relative;
      height: 100%;
      padding: 0 24px 0 10px;
      font-size: 12px;
      color: @default-color;
      cursor: pointer;
      background-color: white;
      border: 1px solid #c4c6cc;

      &:hover {
        border-color: #979ba5;
      }

      .db-textarea-placeholder {
        position: absolute;
        top: 50%;
        display: var(--show-placeholder);
        color: #dcdee5;
        content: attr(placeholder);
        transform: translateY(-50%);
        user-select: none;
      }
    }
  }

  .bk-textarea {
    display: flex;
    min-height: 32px;

    :deep(textarea) {
      min-height: 30px;
      padding: 6px 10px;
      line-height: var(--row-height);
    }
  }
</style>
