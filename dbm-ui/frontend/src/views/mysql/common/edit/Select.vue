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
    ref="rootRef"
    class="table-edit-select"
    :class="{
      'table-edit-select-plain': isPlain,
      'is-focused': isShowPop,
      'is-error': Boolean(errorMessage),
      'is-disabled': disabled,
      'is-seleced': !!localValue,
    }">
    <div
      v-overflow-tips
      class="select-result-text">
      <span>{{ renderText }}</span>
    </div>
    <DbIcon
      v-if="clearable && localValue"
      class="remove-btn"
      type="delete-fill"
      @click.self="handleRemove" />
    <DbIcon
      class="focused-flag"
      type="down-big" />
    <div
      v-if="errorMessage"
      class="select-error">
      <DbIcon
        v-bk-tooltips="errorMessage"
        type="exclamation-fill" />
    </div>
    <div
      v-if="localValue === ''"
      class="select-placeholder">
      {{ placeholder }}
    </div>
    <div style="display: none">
      <div ref="popRef">
        <div
          v-if="searchKey || renderList.length > 0"
          class="search-input-box">
          <BkInput
            v-model="searchKey"
            behavior="simplicity"
            placeholder="请输入字段名搜索">
            <template #prefix>
              <span style="font-size: 14px; color: #979ba5">
                <DbIcon type="search" />
              </span>
            </template>
          </BkInput>
        </div>
        <div class="options-list">
          <div
            v-for="(item, index) in renderList"
            :key="item.id"
            class="option-item"
            :class="{
              active: item.id === localValue,
              disabled: !!item.disabled,
            }"
            @click="handleSelect(item)">
            <slot
              v-if="slots.default"
              :index="index"
              :item="item" />
            <span v-else>{{ item.name }}</span>
          </div>
        </div>
        <div
          v-if="renderList.length < 1"
          style="color: #63656e; text-align: center">
          数据为空
        </div>
        <div
          v-if="slots.footer"
          class="option-footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
  import _ from 'lodash';
  import tippy, { type Instance, type SingleTarget } from 'tippy.js';
  import { computed, onBeforeUnmount, onMounted, ref, useSlots, watch } from 'vue';

  import { useDebouncedRef } from '@hooks';

  import useValidtor, { type Rules } from '@components/render-table/hooks/useValidtor';

  import { encodeRegexp } from '@utils';

  type IKey = string | number;

  export interface IListItem {
    id: IKey;
    name: string;
    disabled?: boolean;
  }

  interface Props {
    modelValue?: IKey;
    list: Array<IListItem>;
    placeholder?: string;
    rules?: Rules;
    disabled?: boolean;
    clearable?: boolean;
    popWidth?: number;
    isPlain?: boolean;
  }
  interface Emits {
    (e: 'update:modelValue', value: IKey): void;
    (e: 'change', value: IKey): void;
  }

  interface Exposes {
    getValue: () => Promise<IKey>;
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: '',
    placeholder: '请选择',
    textarea: false,
    rules: () => [],
    disabled: false,
    clearable: false,
    popWidth: 0,
    isPlain: false,
  });
  const emits = defineEmits<Emits>();

  let tippyIns: Instance;

  const { message: errorMessage, validator } = useValidtor(props.rules);

  const rootRef = ref();
  const popRef = ref();
  const localValue = ref<IKey>('');
  const isShowPop = ref(false);
  const isError = ref(false);

  const slots = useSlots();
  const searchKey = useDebouncedRef('');

  const renderList = computed(() =>
    props.list.reduce((result, item) => {
      const reg = new RegExp(encodeRegexp(searchKey.value), 'i');
      if (reg.test(item.name)) {
        result.push(item);
      }
      return result;
    }, [] as Array<IListItem>),
  );

  const renderText = computed(() => {
    const selectItem = _.find(renderList.value, (item) => item.id === localValue.value);

    return selectItem ? selectItem.name : '';
  });

  watch(
    () => props.modelValue,
    () => {
      localValue.value = props.modelValue;
    },
    {
      immediate: true,
    },
  );

  // 选择
  const handleSelect = (item: IListItem) => {
    if (item.disabled) {
      return;
    }
    localValue.value = item.id;
    tippyIns.hide();

    validator(localValue.value).then(() => {
      window.changeConfirm = true;
      emits('update:modelValue', localValue.value);
      emits('change', localValue.value);
    });
  };
  // 删除值
  const handleRemove = () => {
    localValue.value = '';
    validator(localValue.value).then(() => {
      window.changeConfirm = true;
      emits('update:modelValue', localValue.value);
      emits('change', localValue.value);
    });
  };

  onMounted(() => {
    const theme = ['table-edit-select', 'light'];
    if (slots.footer) {
      theme.push('table-edit-select-footer');
    }
    tippyIns = tippy(rootRef.value as SingleTarget, {
      content: popRef.value,
      placement: 'bottom',
      appendTo: () => document.body,
      theme: theme.join(' '),
      maxWidth: 'none',
      trigger: 'click',
      interactive: true,
      arrow: false,
      offset: [0, 8],
      onShow: () => {
        const { width } = rootRef.value.getBoundingClientRect();
        Object.assign(popRef.value.style, {
          width: `${props.popWidth ? Math.max(props.popWidth, width) : width}px`,
        });
        isShowPop.value = true;
        isError.value = false;
      },
      onHide: () => {
        isShowPop.value = false;
        searchKey.value = '';
        validator(localValue.value);
      },
    });
  });

  onBeforeUnmount(() => {
    if (tippyIns) {
      tippyIns.hide();
      tippyIns.unmount();
      tippyIns.destroy();
    }
  });

  defineExpose<Exposes>({
    getValue() {
      return validator(localValue.value).then(() => localValue.value);
    },
  });
</script>
<style lang="less">
  .table-edit-select {
    position: relative;
    display: flex;
    width: 100%;
    height: 42px;
    overflow: hidden;
    color: #63656e;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.15s;
    align-items: center;

    &:hover {
      background-color: #fafbfd;
      border-color: #a3c5fd;
    }

    &.is-seleced {
      &:hover {
        .remove-btn {
          display: block;
        }

        .focused-flag {
          display: none;
        }
      }
    }

    &.is-focused {
      border: 1px solid #3a84ff;

      .focused-flag {
        transform: rotateZ(-90deg);
      }
    }

    &.is-error {
      background: rgb(255 221 221 / 20%);

      .focused-flag {
        display: none;
      }
    }

    &.is-disabled {
      pointer-events: none;
      cursor: not-allowed;
      background-color: #fafbfd;
    }

    .select-result-text {
      width: 100%;
      height: 100%;
      margin-right: 16px;
      margin-left: 16px;
      overflow: hidden;
      line-height: 42px;
      text-overflow: ellipsis;
      white-space: pre;
    }

    .focused-flag {
      position: absolute;
      right: 4px;
      font-size: 14px;
      transition: all 0.15s;
    }

    .remove-btn {
      position: absolute;
      right: 4px;
      z-index: 1;
      display: none;
      font-size: 16px;
      color: #c4c6cc;
      transition: all 0.15s;

      &:hover {
        color: #979ba5;
      }
    }

    .select-error {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      display: flex;
      padding-right: 4px;
      font-size: 14px;
      color: #ea3636;
      align-items: center;
    }

    .select-placeholder {
      position: absolute;
      top: 10px;
      right: 20px;
      left: 18px;
      z-index: 1;
      height: 20px;
      overflow: hidden;
      font-size: 12px;
      line-height: 20px;
      color: #c4c6cc;
      text-overflow: ellipsis;
      white-space: nowrap;
      pointer-events: none;
    }
  }

  .table-edit-select-plain {
    &.table-edit-select {
      height: 22px;
      border-bottom: 1px solid #c4c6cc;

      &:hover {
        background-color: #fafbfd;
        border: 1px solid transparent;
        border-bottom: 1px solid #a3c5fd;
      }

      &.is-focused {
        border: 1px solid transparent;
        border-bottom: 1px solid #3a84ff;
      }

      .select-result-text {
        margin-left: 2px;
        line-height: 22px;
      }

      .select-placeholder {
        top: 0;
        left: 2px;
      }
    }
  }

  .tippy-box[data-theme~='table-edit-select'] {
    .tippy-content {
      padding: 8px 0;
      font-size: 12px;
      line-height: 32px;
      color: #26323d;
      background-color: #fff;
      border: 1px solid #dcdee5;
      border-radius: 2px;
      user-select: none;

      .search-input-box {
        padding: 0 12px;

        .bk-input--text {
          background-color: #fff;
        }
      }

      .options-list {
        max-height: 300px;
        margin-top: 8px;
        overflow-y: auto;
      }

      .option-item {
        height: 32px;
        padding: 0 12px;
        overflow: hidden;
        line-height: 32px;
        text-overflow: ellipsis;
        white-space: pre;

        &:hover {
          color: #3a84ff;
          cursor: pointer;
          background-color: #f5f7fa;
        }

        &.active {
          color: #3a84ff;
        }

        &.disabled {
          color: #c4c6cc;
          cursor: not-allowed;
          background-color: transparent;
        }
      }

      .option-item-value {
        padding-left: 8px;
        overflow: hidden;
        color: #979ba5;
        text-overflow: ellipsis;
        word-break: keep-all;
        white-space: nowrap;
      }

      .option-footer {
        height: 40px;
        background-color: #fafbfd;
        border-top: 1px solid #dcdee5;
      }
    }
  }

  .tippy-box[data-theme~='table-edit-select-footer'] {
    .tippy-content {
      padding: 8px 0 0;
    }
  }
</style>
