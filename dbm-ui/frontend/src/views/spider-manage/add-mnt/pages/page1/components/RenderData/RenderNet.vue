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
  <RenderText
    ref="editRef"
    :data="clusterData?.bkCloudName"
    :placeholder="t('请先输入集群')"
    :rules="rules" />
</template>
<script setup lang="ts">
  import { ref } from 'vue';
  import { useI18n } from 'vue-i18n';

  import RenderText from '@components/render-table/columns/text-plain/index.vue';

  import type { IDataRow } from './Row.vue';

  interface Props {
    clusterData: IDataRow['clusterData'];
  }

  interface Exposes {
    getValue: (field: string) => Promise<string>;
  }

  const props = defineProps<Props>();

  const { t } = useI18n();

  const editRef = ref();

  const rules = [
    {
      validator: (value: string) => Boolean(value),
      message: t('管控区域不能为空'),
    },
  ];

  defineExpose<Exposes>({
    getValue() {
      return editRef.value.getValue().then(() => ({
        bk_cloud_id: props.clusterData!.bkCloudId,
      }));
    },
  });
</script>
