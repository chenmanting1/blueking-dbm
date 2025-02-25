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
      <span class="ticket-details__item-label">{{ $t('分组名') }}：</span>
      <span class="ticket-details__item-value">{{ ticketDetails?.details?.group_name || '--' }}</span>
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
        <span class="ticket-details__item-label">{{ $t('服务器') }}：</span>
        <span class="ticket-details__item-value">
          <span
            v-if="getServiceNums() > 0"
            class="host-nums"
            @click="handleShowPreview()">
            <a href="javascript:">{{ getServiceNums() }}</a>
            {{ $t('台') }}
          </span>
          <template v-else>--</template>
        </span>
      </div>
    </template>
    <template v-if="ticketDetails?.details?.ip_source === 'resource_pool'">
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('规格') }}：</span>
        <span class="ticket-details__item-value">
          <BkPopover
            placement="top"
            theme="light">
            <span
              class="pb-2"
              style="cursor: pointer; border-bottom: 1px dashed #979ba5">
              {{ influxdbSpec?.spec_name }}（{{ `${influxdbSpec?.count} ${$t('台')}` }}）
            </span>
            <template #content>
              <SpecInfos :data="influxdbSpec" />
            </template>
          </BkPopover>
        </span>
      </div>
    </template>
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

  interface TicketDetails {
    id: number;
    bk_biz_id: number;
    remark: string;
    ticket_type: string;
    bk_biz_name: string;
    db_app_abbr: string;
    details: {
      group_name: string;
      bk_cloud_id: string;
      ip_source: string;
      db_app_abbr: string;
      city_code: string;
      db_version: string;
      port: number;
      group_id: string;
      disaster_tolerance_level: string;
      nodes: {
        influxdb: [];
      };
      resource_spec: {
        influxdb: SpecInfo;
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

  const influxdbSpec = computed(() => props.ticketDetails?.details?.resource_spec?.influxdb || {});

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
  function getServiceNums() {
    const nodes = props.ticketDetails?.details?.nodes;
    return nodes?.influxdb?.length ?? 0;
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

  function handleShowPreview() {
    previewState.isShow = true;
    previewState.role = 'influxdb';
    previewState.title = `【InfluxDB】${t('主机预览')}`;
  }
</script>

<style lang="less" scoped>
  @import '@views/tickets/common/styles/ticketDetails.less';
</style>
