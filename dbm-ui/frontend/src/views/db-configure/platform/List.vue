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
  <div class="platform-db-configure-page">
    <ClusterTab v-model="state.clusterType" />
    <ApplyPermissionCatch :key="state.clusterType">
      <div class="configure-content">
        <BkTab
          v-show="showTabs"
          v-model:active="state.confType"
          class="conf-tabs"
          type="border-card"
          @change="fetchPlatformConfigList">
          <BkTabPanel
            v-for="tab of state.tabs"
            :key="tab.confType"
            :label="tab.name"
            :name="tab.confType" />
        </BkTab>
        <BkLoading :loading="state.loading">
          <DbOriginalTable
            :key="state.clusterType"
            class="configure-content-table"
            :columns="columns"
            :data="state.data"
            :is-anomalies="isAnomalies"
            :max-height="tableMaxHeight"
            @refresh="fetchPlatformConfigList(state.confType)" />
        </BkLoading>
      </div>
    </ApplyPermissionCatch>
  </div>
</template>

<script setup lang="tsx">
  import type { Column } from 'bkui-vue/lib/table/props';
  import { useI18n } from 'vue-i18n';
  import {
    useRoute,
    useRouter,
  } from 'vue-router';

  import { getPlatformConfigList } from '@services/source/configs';

  import { useTableMaxHeight } from '@hooks';

  import { ClusterTypes } from '@common/const';

  import ApplyPermissionCatch from '@components/apply-permission/Catch.vue';
  import ClusterTab from "@components/cluster-tab/Index.vue";

  import { extraClusterConfs, getDefaultConf } from '../common/const';
  import type { ConfType } from '../common/types';

  type ConfigListItem = ServiceReturnType<typeof getPlatformConfigList>

  const { t } = useI18n();
  const route = useRoute();
  const router = useRouter();

  const state = reactive({
    confType: 'dbconf',
    clusterType: '',
    loading: false,
    data: [] as ConfigListItem,
    tabs: [] as ConfType[],
  });
  const isAnomalies = ref(false);
  const showTabs = computed(() => state.tabs.length > 1);
  const occupiedInnerHeight = computed(() => (showTabs.value ? 260 : 194));
  const tableMaxHeight = useTableMaxHeight(occupiedInnerHeight);

  /**
   * table 设置
   */
  const columns: Column[] = [
    {
      label: t('名称'),
      field: 'name',
      render: ({ cell, data }: { cell: string, data: ConfigListItem[number] }) => (
        <bk-button
          text
          theme="primary"
          onClick={() => handleToDetails(data)}>
          {cell}
        </bk-button>
      ),
    },
    {
      label: t('数据库版本'),
      field: 'version',
    },
    {
      label: t('更新时间'),
      field: 'updated_at',
      width: 250,
    },
    {
      label: t('更新人'),
      field: 'updated_by',
      width: 120,
      render: ({ cell }: { cell: string }) => cell || '--',
    },
    {
      label: t('操作'),
      field: 'operation',
      width: 80,
      render: ({ data }: { data: ConfigListItem[number] }) => (
        <div class="operation">
          <bk-button
            text
            theme="primary"
            class="mr-24"
            onClick={() => handleUpdateDetails(data)}>
            { t('编辑') }
          </bk-button>
        </div>
      ),
    },
  ];

  /**
   * 查看详情
   */
  const handleToDetails = (row: ConfigListItem[number]) => {
    router.push({
      name: 'PlatformDbConfigureDetail',
      params: {
        clusterType: state.clusterType,
        confType: state.confType,
        version: row.version,
      },
      query: {
        from: route.name as string,
      },
    });
  };

  /**
   * 编辑配置
   */
  const handleUpdateDetails = (row: ConfigListItem[number]) => {
    router.push({
      name: 'PlatformDbConfigureEdit',
      params: {
        clusterType: state.clusterType,
        confType: state.confType,
        version: row.version,
      },
      query: {
        from: route.name as string,
      },
    });
  };

  /**
   * 获取平台配置列表
   */
  const fetchPlatformConfigList = (confType: string) => {
    if (state.clusterType === '') return;

    state.loading = true;

    getPlatformConfigList({
      meta_cluster_type: state.clusterType,
      conf_type: confType,
    }, {
      permission: 'catch',
    })
      .then((res) => {
        state.data = res || [];
        isAnomalies.value = false;
      })
      .catch(() => {
        state.data = [];
        isAnomalies.value = true;
      })
      .finally(() => {
        state.loading = false;
      });
  };

  /**
   * 集群配置
   */
  watch(() => state.clusterType, (type) => {
    const clusterType = type as ClusterTypes;
    const tabs = [getDefaultConf(clusterType)];
    // 添加额外配置
    const item = extraClusterConfs[clusterType];
    if (item) {
      tabs.push(...item);
    }
    state.tabs = tabs;
    state.confType = 'dbconf';
    router.replace({
      params: {
        clusterType,
      },
    });
    fetchPlatformConfigList(state.confType);
  }, {
    immediate: true,
  });
</script>

<style lang="less">
  .platform-db-configure-page {
    height: calc(100vh - 150px);

    .conf-tabs {
      background: #fff;
      box-shadow: 0 3px 4px 0 rgb(0 0 0 / 4%);

      .bk-tab-content {
        display: none;
      }
    }

    .configure-content {
      padding: 24px;

      .configure-content-table {
        .table-header-type {
          line-height: 20px;
          border-bottom: 1px dashed @light-gray;
        }
      }
    }
  }
</style>
