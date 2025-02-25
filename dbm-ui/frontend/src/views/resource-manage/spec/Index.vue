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
  <div class="resource-spec-list-page">
    <ClusterTab v-model="curTab" />
    <div
      :key="curTab"
      class="wrapper">
      <BkTab
        v-model:active="curChildTab"
        type="card">
        <BkTabPanel
          v-for="childTab of childrenTabs"
          :key="childTab.name"
          :label="childTab.label"
          :name="childTab.name" />
      </BkTab>
      <SpecList
        :cluster-type="curTab"
        :cluster-type-label="clusterTypeLabel"
        :machine-type="curChildTab"
        :machine-type-label="machineTypeLabel" />
    </div>
  </div>
</template>
<script setup lang="ts">
  import { useI18n } from 'vue-i18n';

  import type {
    ControllerBaseInfo,
    ExtractedControllerDataKeys,
    FunctionKeys,
  } from '@services/model/function-controller/functionController';

  import { useFunController } from '@stores';

  import { ClusterTypes } from '@common/const';

  import ClusterTab from '@components/cluster-tab/Index.vue';

  import SpecList from './components/SpecList.vue';

  interface TabItem {
    moduleId: ExtractedControllerDataKeys;
    label: string;
    name: FunctionKeys;
    children: {
      label: string;
      name: string;
    }[];
  }

  const { t } = useI18n();
  const route = useRoute();
  const funControllerStore = useFunController();

  const tabs: TabItem[] = [
    {
      moduleId: 'mysql',
      label: t('MySQL单节点'),
      name: ClusterTypes.TENDBSINGLE,
      children: [
        {
          label: t('后端存储机型'),
          name: 'single',
        },
      ],
    },
    {
      moduleId: 'mysql',
      label: t('MySQL主从'),
      name: ClusterTypes.TENDBHA,
      children: [
        {
          label: t('后端存储机型'),
          name: 'backend',
        },
        {
          label: t('Proxy机型'),
          name: 'proxy',
        },
      ],
    },
    {
      moduleId: 'redis',
      label: 'TendisCache',
      name: ClusterTypes.TWEMPROXY_REDIS_INSTANCE,
      children: [
        {
          label: t('后端存储机型'),
          name: 'tendiscache',
        },
        {
          label: t('Proxy机型'),
          name: 'twemproxy',
        },
      ],
    },
    {
      moduleId: 'redis',
      label: 'TendisSSD',
      name: ClusterTypes.TWEMPROXY_TENDIS_SSD_INSTANCE,
      children: [
        {
          label: t('后端存储机型'),
          name: 'tendisssd',
        },
        {
          label: t('Proxy机型'),
          name: 'twemproxy',
        },
      ],
    },
    {
      moduleId: 'redis',
      label: 'Tendisplus',
      name: ClusterTypes.PREDIXY_TENDISPLUS_CLUSTER,
      children: [
        {
          label: t('后端存储机型'),
          name: 'tendisplus',
        },
        {
          label: t('Proxy机型'),
          name: 'predixy',
        },
      ],
    },
    {
      moduleId: 'redis',
      label: 'RedisCluster',
      name: ClusterTypes.PREDIXY_REDIS_CLUSTER,
      children: [
        {
          label: t('后端存储机型'),
          name: 'tendiscache',
        },
        {
          label: t('Proxy机型'),
          name: 'predixy',
        },
      ],
    },
    {
      moduleId: 'redis',
      label: t('Redis主从'),
      name: ClusterTypes.REDIS_INSTANCE,
      children: [
        {
          label: t('后端存储机型'),
          name: 'tendiscache',
        },
      ],
    },
    {
      moduleId: 'bigdata',
      label: 'ES',
      name: ClusterTypes.ES,
      children: [
        {
          label: t('Master节点规格'),
          name: 'es_master',
        },
        {
          label: t('Client节点规格'),
          name: 'es_client',
        },
        {
          label: t('冷_热节点规格'),
          name: 'es_datanode',
        },
      ],
    },
    {
      moduleId: 'bigdata',
      label: 'HDFS',
      name: ClusterTypes.HDFS,
      children: [
        {
          label: t('DataNode节点规格'),
          name: 'hdfs_datanode',
        },
        {
          label: t('NameNode_Zookeeper_JournalNode节点规格'),
          name: 'hdfs_master',
        },
      ],
    },
    {
      moduleId: 'bigdata',
      label: 'Kafka',
      name: ClusterTypes.KAFKA,
      children: [
        {
          label: t('Zookeeper节点规格'),
          name: 'zookeeper',
        },
        {
          label: t('Broker节点规格'),
          name: 'broker',
        },
      ],
    },
    {
      moduleId: 'bigdata',
      label: 'InfluxDB',
      name: ClusterTypes.INFLUXDB,
      children: [
        {
          label: t('后端存储机型'),
          name: 'influxdb',
        },
      ],
    },
    {
      moduleId: 'bigdata',
      label: 'Pulsar',
      name: ClusterTypes.PULSAR,
      children: [
        {
          label: t('Bookkeeper节点规格'),
          name: 'pulsar_bookkeeper',
        },
        {
          label: t('Zookeeper节点规格'),
          name: 'pulsar_zookeeper',
        },
        {
          label: t('Broker节点规格'),
          name: 'pulsar_broker',
        },
      ],
    },
    {
      moduleId: 'mysql',
      label: 'TenDBCluster',
      name: ClusterTypes.TENDBCLUSTER,
      children: [
        {
          label: t('接入层Master'),
          name: 'spider',
        },
        {
          label: t('后端存储规格'),
          name: 'remote',
        },
      ],
    },
    {
      moduleId: 'bigdata',
      label: 'Riak',
      name: ClusterTypes.RIAK,
      children: [
        {
          label: t('后端存储机型'),
          name: 'riak',
        },
      ],
    },
    {
      moduleId: 'mongodb',
      label: t('Mongo副本集'),
      name: ClusterTypes.MONGO_REPLICA_SET,
      children: [
        {
          label: t('Mongodb规格'),
          name: 'mongodb',
        },
      ],
    },
    {
      moduleId: 'mongodb',
      label: t('Mongo分片集'),
      name: ClusterTypes.MONGO_SHARED_CLUSTER,
      children: [
        {
          label: t('ConfigSvr规格'),
          name: 'mongo_config',
        },
        {
          label: t('Mongos规格'),
          name: 'mongos',
        },
        {
          label: t('ShardSvr规格'),
          name: 'mongodb',
        },
      ],
    },
    {
      moduleId: 'sqlserver',
      label: t('SQLServer单节点'),
      name: ClusterTypes.SQLSERVER_SINGLE,
      children: [
        {
          label: t('后端存储机型'),
          name: 'sqlserver_single',
        },
      ],
    },
    {
      moduleId: 'sqlserver',
      label: t('SQLServer主从'),
      name: ClusterTypes.SQLSERVER_HA,
      children: [
        {
          label: t('后端存储机型'),
          name: 'sqlserver_ha',
        },
      ],
    },
  ];

  const curTab = ref<ClusterTypes>(ClusterTypes.TENDBSINGLE);
  const curChildTab = ref('');

  const renderTabs = computed(() =>
    tabs.filter((item) => {
      const data = funControllerStore.funControllerData[item.moduleId];
      if (!data) {
        return false;
      }

      const childItem = (data.children as Record<TabItem['name'], ControllerBaseInfo>)[item.name];

      // 若有对应的模块子功能，判断是否开启
      if (childItem) {
        return data && data.is_enabled && childItem.is_enabled;
      }

      // 若无，则判断整个模块是否开启
      return data && data.is_enabled;
    }),
  );
  const childrenTabs = computed(() => renderTabs.value.find((item) => item.name === curTab.value)?.children || []);
  const clusterTypeLabel = computed(() => renderTabs.value.find((item) => item.name === curTab.value)?.label ?? '');
  const machineTypeLabel = computed(
    () => childrenTabs.value.find((item) => item.name === curChildTab.value)?.label ?? '',
  );

  watch(curTab, (newVal, oldVal) => {
    if (oldVal !== newVal) {
      curChildTab.value = '';
    }
  });

  onMounted(() => {
    const { spec_cluster_type: clusterType } = route.query;
    if (clusterType) {
      curTab.value = clusterType as ClusterTypes;
    }
  });
</script>
<style lang="less">
  .resource-spec-list-page {
    .bk-tab-content {
      display: none;
    }

    .top-tabs {
      padding: 0 24px;
      background: #fff;
      box-shadow: 0 3px 4px 0 rgb(0 0 0 / 4%);
    }

    .wrapper {
      padding: 24px;
    }
  }
</style>
