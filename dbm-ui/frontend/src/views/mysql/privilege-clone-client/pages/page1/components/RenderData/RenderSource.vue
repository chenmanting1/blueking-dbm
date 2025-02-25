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
    <TableEditInput
      ref="editRef"
      v-model="localValue"
      :placeholder="t('请输入管控区域:IP或从表头批量选择')"
      :rules="rules"
      @submit="handleChange" />
  </BkLoading>
</template>
<script setup lang="ts">
  import _ from 'lodash';
  import { useI18n } from 'vue-i18n';

  import { netIp } from '@common/regex';

  import TableEditInput from '@components/render-table/columns/input/index.vue';

  import type { IDataRow } from './Row.vue';

  interface Exposes {
    getValue: () => Promise<{
      source: string;
      bk_cloud_id: number;
    }>;
  }

  const modelValue = defineModel<IDataRow['source']>();

  const { t } = useI18n();

  const editRef = ref();
  const localValue = ref('');
  const isLoading = ref(false);

  const rules = [
    {
      validator: (value: string) => Boolean(_.trim(value)),
      message: t('源客户端 IP 不能为空'),
    },
    {
      validator: (ip: string) => {
        const items = ip.split(':');
        return items.length === 2 && /^\d+$/.test(items[0]);
      },
      message: t('请输入xx', [t('管控区域')]),
      trigger: 'blur',
    },
    {
      validator: (value: string) => netIp.test(value),
      message: t('源客户端 IP 格式不正确'),
    },
  ];

  watch(
    () => modelValue.value,
    () => {
      if (!modelValue.value) {
        return;
      }
      localValue.value = `${modelValue.value.bk_cloud_id}:${modelValue.value.ip}`;
    },
    {
      immediate: true,
    },
  );

  const handleChange = (value: string) => {
    if (!value) {
      return;
    }

    const [bkCloudId, ip] = value.split(':');
    modelValue.value = {
      ip,
      bk_cloud_id: Number(bkCloudId),
    };
  };

  defineExpose<Exposes>({
    getValue() {
      return editRef.value.getValue().then(() => {
        if (!modelValue.value) {
          return Promise.reject();
        }
        return {
          source: modelValue.value.ip,
          bk_cloud_id: modelValue.value.bk_cloud_id,
        };
      });
    },
  });
</script>
