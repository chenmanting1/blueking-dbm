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
  <strong class="ticket-details__info-title">{{ $t('业务信息') }}</strong>
  <div class="ticket-details__list">
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('所属业务') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.bk_biz_name || '--' }}</span>
    </div>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('业务英文名') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.db_app_abbr || '--' }}</span>
    </div>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('集群名称') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.cluster_name || '--' }}</span>
    </div>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('集群别名') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.cluster_alias || '--' }}</span>
    </div>
  </div>
  <strong class="ticket-details__info-title">{{ $t('地域要求') }}</strong>
  <div class="ticket-details__list">
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('数据库部署地域') }}：</span>
      <span class="ticket-details__item-value">{{ cityName }}</span>
    </div>
  </div>
  <strong class="ticket-details__info-title">{{ $t('数据库部署信息') }}</strong>
  <div class="ticket-details__list">
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('容灾要求') }}：</span>
      <span class="ticket-details__item-value">{{ affinity }}</span>
    </div>
  </div>
  <strong class="ticket-details__info-title">{{ $t('部署需求') }}</strong>
  <div class="ticket-details__list">
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('版本') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.db_version || '--' }}</span>
    </div>
    <template v-if="ticketDetails?.details?.ip_source === redisIpSources.manual_input.id">
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('Bookkeeper节点') }}：</span>
        <span class="ticket-details__item-value">
          <span
            v-if="getServiceNums('bookkeeper') > 0"
            class="host-nums"
            @click="handleShowPreview('bookkeeper')">
            <a href="javascript:">{{ getServiceNums('bookkeeper') }}</a>
            {{ $t('台') }}
          </span>
          <template v-else>--</template>
        </span>
      </div>
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('Zookeeper节点') }}：</span>
        <span class="ticket-details__item-value">
          <span
            v-if="getServiceNums('zookeeper') > 0"
            class="host-nums"
            @click="handleShowPreview('zookeeper')">
            <a href="javascript:">{{ getServiceNums('zookeeper') }}</a>
            {{ $t('台') }}
          </span>
          <template v-else>--</template>
        </span>
      </div>
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('Broker节点') }}：</span>
        <span class="ticket-details__item-value">
          <span
            v-if="getServiceNums('broker') > 0"
            class="host-nums"
            @click="handleShowPreview('broker')">
            <a href="javascript:">{{ getServiceNums('broker') }}</a>
            {{ $t('台') }}
          </span>
          <template v-else>--</template>
        </span>
      </div>
    </template>
    <template v-if="ticketDetails?.details?.ip_source === 'resource_pool'">
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('Bookkeeper节点规格') }}：</span>
        <span class="ticket-details__item-value">
          <BkPopover
            placement="top"
            theme="light">
            <span
              class="pb-2"
              style="cursor: pointer; border-bottom: 1px dashed #979ba5">
              {{ bookkeeperSpec?.spec_name }}（{{ `${bookkeeperSpec?.count} ${$t('台')}` }}）
            </span>
            <template #content>
              <SpecInfos :data="bookkeeperSpec" />
            </template>
          </BkPopover>
        </span>
      </div>
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('Zookeeper节点规格') }}：</span>
        <span class="ticket-details__item-value">
          <BkPopover
            placement="top"
            theme="light">
            <span
              class="pb-2"
              style="cursor: pointer; border-bottom: 1px dashed #979ba5">
              {{ zookeeperSpec?.spec_name }}（{{ `${zookeeperSpec?.count} ${$t('台')}` }}）
            </span>
            <template #content>
              <SpecInfos :data="zookeeperSpec" />
            </template>
          </BkPopover>
        </span>
      </div>
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('Broker节点规格') }}：</span>
        <span class="ticket-details__item-value">
          <BkPopover
            placement="top"
            theme="light">
            <span
              class="pb-2"
              style="cursor: pointer; border-bottom: 1px dashed #979ba5">
              {{ brokerSpec?.spec_name }}（{{ `${brokerSpec?.count} ${$t('台')}` }}）
            </span>
            <template #content>
              <SpecInfos :data="brokerSpec" />
            </template>
          </BkPopover>
        </span>
      </div>
    </template>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('Partition数量') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.partition_num || '--' }}</span>
    </div>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('消息保留') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.retention_hours || '--' }}</span>
    </div>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('副本数量') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.replication_num || '--' }}</span>
    </div>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('至少写入成功副本数量') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.ack_quorum || '--' }}</span>
    </div>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('访问端口') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.port || '--' }}</span>
    </div>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('备注') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.remark || '--' }}</span>
    </div>
  </div>
  <HostPreview
    v-model:is-show="previewState.isShow"
    :fetch-nodes="getTicketHostNodes"
    :fetch-params="fetchNodesParams"
    :title="previewState.title" />
</template>

<script setup lang="ts">
  import { useI18n } from 'vue-i18n';
  import { useRequest } from 'vue-request';

  import { getInfrasCities, getTicketHostNodes } from '@services/source/ticket';

  import { useSystemEnviron } from '@stores';

  import HostPreview from '@components/host-preview/HostPreview.vue';

  import { redisIpSources } from '@views/redis/apply/common/const';

  import SpecInfos, { type SpecInfo } from '../../SpecInfos.vue';

  type ServiceKeys = 'bookkeeper' | 'zookeeper' | 'broker';

  interface TicketDetails {
    id: number;
    bk_biz_id: number;
    remark: string;
    ticket_type: string;
    bk_biz_name: string;
    db_app_abbr: string;
    details: {
      username: string;
      password: string;
      ip_source: string;
      db_version: string;
      retention_hours: number;
      replication_num: number;
      ack_quorum: number;
      port: number;
      partition_num: number;
      cluster_name: string;
      cluster_alias: string;
      city_code: string;
      db_app_abbr: string;
      disaster_tolerance_level: string;
      nodes: {
        zookeeper: [];
        broker: [];
        bookkeeper: [];
      };
      resource_spec: {
        zookeeper: SpecInfo;
        broker: SpecInfo;
        bookkeeper: SpecInfo;
      };
    };
  }

  interface Props {
    ticketDetails: TicketDetails;
  }

  const props = defineProps<Props>();

  const { t } = useI18n();
  const { AFFINITY: affinityList } = useSystemEnviron().urls;

  const cityName = ref('--');

  const zookeeperSpec = computed(() => props.ticketDetails?.details?.resource_spec?.zookeeper || {});
  const bookkeeperSpec = computed(() => props.ticketDetails?.details?.resource_spec?.bookkeeper || {});
  const brokerSpec = computed(() => props.ticketDetails?.details?.resource_spec?.broker || {});

  const affinity = computed(() => {
    const level = props.ticketDetails?.details?.disaster_tolerance_level;
    if (level && affinityList) {
      return affinityList.find((item) => item.value === level)?.label;
    }
    return '--';
  });

  useRequest(getInfrasCities, {
    onSuccess: (cityList) => {
      const cityCode = props.ticketDetails.details.city_code;
      const name = cityList.find((item) => item.city_code === cityCode)?.city_name;
      cityName.value = name ?? '--';
    },
  });

  /**
   * 获取服务器数量
   */
  function getServiceNums(key: ServiceKeys) {
    const nodes = props.ticketDetails?.details?.nodes;
    return nodes?.[key]?.length ?? 0;
  }

  /**
   * 服务器详情预览功能
   */
  const previewState = reactive({
    isShow: false,
    role: '',
    title: t('主机预览'),
  });
  const fetchNodesParams = computed(() => ({
    bk_biz_id: props.ticketDetails.bk_biz_id,
    id: props.ticketDetails.id,
    role: previewState.role,
  }));

  function handleShowPreview(role: ServiceKeys) {
    previewState.isShow = true;
    previewState.role = role;
    const title = role.slice(0, 1).toUpperCase() + role.slice(1);
    previewState.title = `【${title}】${t('主机预览')}`;
  }
</script>

<style lang="less" scoped>
  @import '@views/tickets/common/styles/ticketDetails.less';
</style>
