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
        <span class="ticket-details__item-label">{{ $t('DataNode节点IP') }}：</span>
        <span class="ticket-details__item-value">
          <span
            v-if="getServiceNums('datanode') > 0"
            class="host-nums"
            @click="handleShowPreview('datanode')">
            <a href="javascript:">{{ getServiceNums('datanode') }}</a>
            {{ $t('台') }}
          </span>
          <template v-else>--</template>
        </span>
      </div>
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('NameNode节点IP') }}：</span>
        <span class="ticket-details__item-value">
          <span
            v-if="getServiceNums('namenode') > 0"
            class="host-nums"
            @click="handleShowPreview('namenode')">
            <a href="javascript:">{{ getServiceNums('namenode') }}</a>
            {{ $t('台') }}
          </span>
          <template v-else>--</template>
        </span>
      </div>
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">{{ $t('Zookeeper节点IP') }}：</span>
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
    </template>
    <template v-else>
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">NameNode：</span>
        <span class="ticket-details__item-value">
          <BkPopover
            placement="top"
            theme="light">
            <span
              class="pb-2"
              style="cursor: pointer; border-bottom: 1px dashed #979ba5">
              {{ namenodeSpec?.spec_name }}（{{ `${namenodeSpec?.count} ${$t('台')}` }}）
            </span>
            <template #content>
              <SpecInfos :data="namenodeSpec" />
            </template>
          </BkPopover>
        </span>
      </div>
      <div class="ticket-details__item">
        <span class="ticket-details__item-label">Zookeepers/JournalNodes：</span>
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
        <span class="ticket-details__item-label">DataNodes：</span>
        <span class="ticket-details__item-value">
          <BkPopover
            placement="top"
            theme="light">
            <span
              class="pb-2"
              style="cursor: pointer; border-bottom: 1px dashed #979ba5">
              {{ datanodeSpec?.spec_name }}（{{ `${datanodeSpec?.count} ${$t('台')}` }}）
            </span>
            <template #content>
              <SpecInfos :data="datanodeSpec" />
            </template>
          </BkPopover>
        </span>
      </div>
    </template>
    <div class="ticket-details__item">
      <span class="ticket-details__item-label">{{ $t('备注') }}：</span>
      <span
        v-overflow-tips
        class="ticket-details__item-value">
        {{ ticketDetails?.remark || '--' }}
      </span>
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
  import type { TicketDetails, TicketDetailsHDFS } from '@services/types/ticket';

  import { useSystemEnviron } from '@stores';

  import HostPreview from '@components/host-preview/HostPreview.vue';

  import { redisIpSources } from '@views/redis/apply/common/const';

  import { firstLetterToUpper } from '@utils';

  import SpecInfos, { type SpecInfo } from '../../SpecInfos.vue';

  interface Details extends TicketDetailsHDFS {
    ip_source: string;
    disaster_tolerance_level: string;
    resource_spec: {
      namenode: SpecInfo;
      zookeeper: SpecInfo;
      datanode: SpecInfo;
    };
  }

  interface Props {
    ticketDetails: TicketDetails<Details>;
  }

  const props = defineProps<Props>();

  const { t } = useI18n();
  const { AFFINITY: affinityList } = useSystemEnviron().urls;

  const cityName = ref('--');

  const zookeeperSpec = computed(() => props.ticketDetails?.details?.resource_spec?.zookeeper || {});
  const namenodeSpec = computed(() => props.ticketDetails?.details?.resource_spec?.namenode || {});
  const datanodeSpec = computed(() => props.ticketDetails?.details?.resource_spec?.datanode || {});

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
  function getServiceNums(key: 'datanode' | 'namenode' | 'zookeeper') {
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

  function handleShowPreview(role: 'datanode' | 'namenode' | 'zookeeper') {
    previewState.isShow = true;
    previewState.role = role;
    previewState.title = `【${firstLetterToUpper(role)}】${t('主机预览')}`;
  }
</script>

<style lang="less" scoped>
  @import '@views/tickets/common/styles/ticketDetails.less';
</style>
