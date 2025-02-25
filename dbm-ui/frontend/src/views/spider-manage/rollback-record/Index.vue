<template>
  <BkAlert
    closable
    theme="info"
    :title="$t('构造实例：通过定点构造产生的实例，可以将实例数据写回原集群或者直接销毁')" />
  <div class="mt-16 mb-16">
    <DbPopconfirm
      :confirm-handler="handleBatchDisable"
      :content="t('移除后将不可恢复')"
      :title="t('确认销毁选中的实例')">
      <BkButton :disabled="selectionList.length < 1">
        {{ t('批量销毁') }}
      </BkButton>
    </DbPopconfirm>
  </div>
  <DbTable
    ref="tableRef"
    :columns="tableColumns"
    :data-source="queryFixpointLog"
    :disable-select-method="disableSelectMethodCallback"
    primary-key="target_cluster.cluster_id"
    selectable
    @selection="handleSelectionChange" />
</template>
<script setup lang="tsx">
  import {
    onMounted,
    ref,
  } from 'vue';
  import { useI18n } from 'vue-i18n';

  import FixpointLogModel from '@services/model/fixpoint-rollback/fixpoint-log';
  import { queryFixpointLog } from '@services/source/fixpointRollback';
  import { createTicket } from '@services/source/ticket';

  import { useTicketMessage } from '@hooks';

  import { useGlobalBizs } from '@stores';

  const { t } = useI18n();
  const { currentBizId } = useGlobalBizs();
  const ticketMessage = useTicketMessage();

  const tableRef = ref();
  const selectionList = ref<string[]>([]);

  const tableColumns = [
    {
      label: t('源集群'),
      showOverflowTooltip: true,
      width: 200,
      render: ({ data }: {data: FixpointLogModel}) => data.source_cluster.immute_domain,
    },
    {
      label: t('构造主机'),
      showOverflowTooltip: true,
      minWidth: 200,
      render: ({ data }: {data: FixpointLogModel}) => data.ipText || '--',
    },
    {
      label: t('回档类型'),
      showOverflowTooltip: true,
      minWidth: 200,
      render: ({ data }: {data: FixpointLogModel}) => data.rollbackTypeText,
    },
    {
      label: t('构造 DB 名'),
      showOverflowTooltip: true,
      minWidth: 100,
      render: ({ data }: {data: FixpointLogModel}) => (data.databases.length < 1 ? '--' : (
        <>
          {
            data.databases.map(item => (
              <bk-tag>{item}</bk-tag>
            ))
          }
        </>
      )),
    },
    {
      label: t('忽略 DB 名'),
      showOverflowTooltip: true,
      minWidth: 100,
      render: ({ data }: {data: FixpointLogModel}) => (data.databases_ignore.length < 1 ? '--' : (
        <>
          {
            data.databases_ignore.map(item => (
              <bk-tag>{item}</bk-tag>
            ))
          }
        </>
      )),
    },
    {
      label: t('构造表名'),
      showOverflowTooltip: true,
      minWidth: 100,
      render: ({ data }: {data: FixpointLogModel}) => (data.tables.length < 1 ? '--' : (
        <>
          {
            data.tables.map(item => (
              <bk-tag>{item}</bk-tag>
            ))
          }
        </>
      )),
    },
    {
      label: t('忽略表名'),
      showOverflowTooltip: true,
      minWidth: 100,
      render: ({ data }: {data: FixpointLogModel}) => (data.tables_ignore.length < 1 ? '--' : (
        <>
          {
            data.tables_ignore.map(item => (
              <bk-tag>{item}</bk-tag>
            ))
          }
        </>
      )),
    },
    {
      label: t('关联单据'),
      showOverflowTooltip: true,
      width: 90,
      render: ({ data }: {data: FixpointLogModel}) => (
        <router-link
          to={{
            name: 'bizTicketManage',
            query: {
              id: data.ticket_id,
            },
          }}
          target="_blank">
          {data.ticket_id}
        </router-link>
      ),
    },
    {
      label: t('操作'),
      width: 100,
      fixed: 'right',
      render: ({ data }: {data: FixpointLogModel}) => (
        <db-popconfirm
          confirm-handler={() => handleDestroy(data)}
          content={t('移除后将不可恢复')}
          title={t('确认销毁选中的实例')}>
          <bk-button
            theme="primary"
            disabled={!data.isDestoryEnable}
            text>
            {t('销毁')}
          </bk-button>
        </db-popconfirm>
      ),
    },
  ];

  const fetchData = () => {
    tableRef.value.fetchData();
  };

  const disableSelectMethodCallback = (data: FixpointLogModel) => !data.isDestoryEnable;

  const handleDestroy = (payload: FixpointLogModel) => createTicket({
    bk_biz_id: currentBizId,
    remark: '',
    ticket_type: 'TENDBCLUSTER_TEMPORARY_DESTROY',
    details: {
      cluster_ids: [payload.target_cluster.cluster_id],
    },
  }).then((data) => {
    ticketMessage(data.id);
    fetchData();
  });

  const handleSelectionChange = (payload: string[]) => {
    selectionList.value = payload;
  };

  const handleBatchDisable = () => createTicket({
    bk_biz_id: currentBizId,
    remark: '',
    ticket_type: 'TENDBCLUSTER_TEMPORARY_DESTROY',
    details: {
      cluster_ids: selectionList.value,
    },
  })
    .then((data) => {
      ticketMessage(data.id);
      fetchData();
    });

  onMounted(() => {
    fetchData();
  });
</script>
