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
  <div class="render-host-box">
    <TableEditInput
      ref="editRef"
      v-model="localValue"
      :placeholder="t('请输入IP（单个）')"
      :rules="rules"
      @submit="handleInputFinish" />
  </div>
</template>
<script setup lang="ts">
  import { useI18n } from 'vue-i18n';

  import { ipv4 } from '@common/regex';

  import TableEditInput from '@components/render-table/columns/input/index.vue';

  import type { IDataRow } from './Row.vue';

  interface Props {
    modelValue?: IDataRow['ip'];
  }

  interface Emits {
    (e: 'onInputFinish', value: string): void;
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: '',
  });
  const emits = defineEmits<Emits>();

  const { t } = useI18n();
  const localValue = ref(props.modelValue);
  const editRef = ref();

  const rules = [
    {
      validator: (value: string) => Boolean(value),
      message: t('IP不能为空'),
    },
    {
      validator: (value: string) => ipv4.test(value),
      message: t('IP格式不正确'),
    },
  ];

  const handleInputFinish = (value: string) => {
    editRef.value.getValue().then(() => {
      emits('onInputFinish', value);
    });
  };
</script>
<style lang="less" scoped>
  .render-host-box {
    position: relative;
  }
</style>
