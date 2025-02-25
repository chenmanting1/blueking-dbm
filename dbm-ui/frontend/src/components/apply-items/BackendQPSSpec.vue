<template>
  <div class="redis-backend-spec">
    <BkFormItem
      :label="t('部署方案选择')"
      required>
      <BkRadioGroup
        v-model="applyType"
        style="width: 314px">
        <BkRadioButton
          label="auto"
          style="flex: 1">
          {{ t('自动推荐方案') }}
          <BkTag
            size="small"
            theme="success">
            {{ t('实验') }}
          </BkTag>
        </BkRadioButton>
        <BkRadioButton
          label="custom"
          style="flex: 1">
          {{ t('自定义方案') }}
        </BkRadioButton>
      </BkRadioGroup>
    </BkFormItem>
    <template v-if="applyType === 'auto'">
      <BkFormItem
        :label="t('集群容量需求')"
        property="details.resource_spec.backend_group.capacity"
        required>
        <BkInput
          :min="1"
          :model-value="modelValue.capacity"
          style="width: 314px"
          type="number"
          @blur="handleBlurCapacity"
          @change="handleChangeCapacity"
          @focus="handleFocusCapacity" />
        <span class="input-desc">G</span>
      </BkFormItem>
      <BkFormItem
        :label="t('未来集群容量需求')"
        property="details.resource_spec.backend_group.future_capacity"
        required>
        <BkInput
          :min="Number(modelValue.capacity)"
          :model-value="modelValue.future_capacity"
          style="width: 314px"
          type="number"
          @blur="handleBlurCapacity"
          @change="handleChangeFutureCapacity"
          @focus="handleFocusCapacity" />
        <span class="input-desc">G</span>
      </BkFormItem>
      <BkFormItem
        :label="t('QPS预估范围')"
        required>
        <BkSlider
          v-model="sliderProps.value"
          :disable="sliderProps.disabled"
          :formatter-label="formatterLabel"
          :max-value="sliderProps.max"
          :min-value="sliderProps.min"
          range
          show-between-label
          show-input
          show-tip
          style="width: 800px; font-size: 12px" />
      </BkFormItem>
      <BkFormItem
        ref="specRef"
        :label="t('集群部署方案')"
        property="details.resource_spec.backend_group.spec_id"
        required>
        <DbOriginalTable
          v-bkloading="{ loading: isLoading }"
          class="custom-edit-table"
          :columns="columns"
          :data="renderSpecs"
          @row-click="handleRowClick">
          <template #empty>
            <p
              v-if="!sliderProps.value[1]"
              style="width: 100%; line-height: 128px; text-align: center">
              <DbIcon
                class="mr-4"
                type="attention" />
              <span>{{ t('请先设置容量及QPS范围') }}</span>
            </p>
            <BkException
              v-else
              :description="t('无匹配的资源规格_请先修改容量及QPS设置')"
              scene="part"
              style="font-size: 12px"
              type="empty" />
          </template>
        </DbOriginalTable>
      </BkFormItem>
    </template>
    <template v-else>
      <BkFormItem
        :label="t('规格')"
        property="details.resource_spec.backend_group.spec_id"
        required>
        <SpecSelector
          ref="specSelectorRef"
          v-model="modelValue.spec_id"
          :biz-id="bizId"
          :cloud-id="cloudId"
          :cluster-type="ClusterTypes.TENDBCLUSTER"
          machine-type="remote"
          style="width: 314px" />
      </BkFormItem>
      <BkFormItem
        :label="t('数量')"
        property="details.resource_spec.backend_group.count"
        required>
        <BkInput
          v-model="modelValue.count"
          clearable
          :min="1"
          show-clear-only-hover
          style="width: 314px"
          type="number" />
        <span class="input-desc">{{ t('组') }}</span>
      </BkFormItem>
      <BkFormItem
        :label="t('单机分片数')"
        required>
        <BkInput
          v-model="shardNum"
          :min="1"
          style="width: 314px"
          type="number" />
      </BkFormItem>
      <BkFormItem
        :label="t('集群分片数')"
        :required="false">
        <BkInput
          v-model="clusterShardNum"
          disabled
          :placeholder="t('自动生成')"
          style="width: 314px"
          type="number" />
      </BkFormItem>
      <BkFormItem
        :label="t('总容量')"
        :required="false">
        <BkInput
          v-model="specInfo.totalCapcity"
          disabled
          :placeholder="t('自动生成')"
          style="width: 314px"
          type="number" />
        <span class="input-desc">G</span>
      </BkFormItem>
      <BkFormItem
        :label="t('QPS')"
        :required="false">
        <BkInput
          v-model="specInfo.qps"
          disabled
          :placeholder="t('自动生成')"
          style="width: 314px"
          type="number" />
        <span class="input-desc">/s</span>
      </BkFormItem>
    </template>
  </div>
</template>

<script setup lang="tsx">
  import _ from 'lodash';
  import { useI18n } from 'vue-i18n';

  import ClusterSpecModel from '@services/model/resource-spec/cluster-sepc';
  import ResourceSpecModel from '@services/model/resource-spec/resourceSpec';
  import { getSpecResourceCount } from '@services/source/dbresourceResource';
  import {
    getFilterClusterSpec,
    queryQPSRange,
  } from '@services/source/dbresourceSpec';

  import { ClusterTypes } from '@common/const';

  import SpecSelector from '@components/apply-items/SpecSelector.vue';

  interface ModelValue {
    spec_id: number | string,
    capacity: number | string,
    count: number,
    future_capacity: number | string,
  }

  interface Props {
    clusterType: string,
    machineType: string,
    bizId: number | string,
    cloudId: number | string,
  }

  const props = defineProps<Props>();
  const modelValue = defineModel<ModelValue>({ required: true });

  const { t } = useI18n();

  const specRef = ref();
  const specSelectorRef = ref<InstanceType<typeof SpecSelector>>()
  const specs = shallowRef<ClusterSpecModel[]>([]);
  const renderSpecs = shallowRef<ClusterSpecModel[]>([]);
  const isLoading = ref(false);
  const sliderProps = reactive({
    value: [0, 0],
    max: 0,
    min: 0,
    disabled: true,
  });

  const applyType = ref('auto')
  const shardNum = ref(1)

  const columns = [
    {
      field: 'spec_name',
      label: t('资源规格'),
      showOverflowTooltip: false,
      render: ({ data, index }: { data: ClusterSpecModel, index: number }) => (
        <bk-radio
          v-model={modelValue.value.spec_id}
          label={data.spec_id}
          kye={index}
          class="spec-radio">
          <div
            class="text-overflow"
            v-overflow-tips>
            {data.spec_name}
          </div>
        </bk-radio>
        ),
    },
    {
      field: 'machine_pair',
      label: t('需机器组数'),
      sort: true,
    },
    {
      field: 'cluster_shard_num',
      label: t('集群分片'),
      sort: true,
    },
    {
      field: 'cluster_capacity',
      label: t('集群容量G'),
      sort: true,
    },
    {
      field: 'cluster_qps',
      label: t('集群QPS每秒'),
    },
    {
      field: 'count',
      label: t('可用主机数'),
    },
  ];

  const clusterShardNum = computed(() => modelValue.value.count * shardNum.value || '')

  const specInfo = computed(() => {
    const data = specSelectorRef.value?.getData()
    const {count} = modelValue.value

    if (_.isEmpty(data)) {
      return {
        totalCapcity: '',
        qps: ''
      }
    }

    return {
      totalCapcity: count * getSpecCapacity(data.storage_spec),
      qps: count * (data.qps.min ?? 0)
    }
  })

  const getSpecCapacity = (storageSpec: ResourceSpecModel['storage_spec']) => {
    let specCapacity = 0
    for (let i = 0; i < storageSpec.length; i++) {
      const storageSpecItem = storageSpec[i]
      if (storageSpecItem.mount_point === '/data1') {
        return storageSpecItem.size
      }
      if (storageSpecItem.mount_point === '/data') {
        specCapacity = storageSpecItem.size / 2
      }
    }
    return specCapacity
  }

  const formatterLabel = (value: string) => `${value}/s`;

  const resetSlider = () => {
    sliderProps.value = [0, 0];
    sliderProps.max = 0;
    sliderProps.min = 0;
    sliderProps.disabled = true;
    specs.value = [];
    renderSpecs.value = [];
  };

  const fetchQPSRange = _.debounce(() => {
    const { capacity, future_capacity: futureCapacity } = modelValue.value;
    if (!capacity || !futureCapacity) {
      resetSlider();
      return;
    }

    queryQPSRange({
      spec_cluster_type: props.clusterType,
      spec_machine_type: props.machineType,
      capacity: Number(capacity),
      future_capacity: Number(futureCapacity),
    })
      .then(({ max, min }) => {
        if (!max || !min) {
          sliderProps.max = 0;
          sliderProps.min = 0;
          sliderProps.disabled = true;
        }
        sliderProps.value = [min, max];
        sliderProps.max = max;
        sliderProps.min = min;
      });
  }, 400);

  const fetchFilterClusterSpec = () => {
    const { capacity, future_capacity: futureCapacity } = modelValue.value;
    const [min, max] = sliderProps.value;

    if (!capacity || !futureCapacity || (max === 0)) {
      return;
    }

    isLoading.value = true;
    getFilterClusterSpec({
      spec_cluster_type: props.clusterType,
      spec_machine_type: props.machineType,
      capacity: Number(capacity),
      future_capacity: Number(futureCapacity),
      qps: { min, max },
    })
      .then((res) => {
        specs.value = res;
        renderSpecs.value = res;
      })
      .catch(() => {
        specs.value = [];
        renderSpecs.value = [];
      })
      .finally(() => {
        isLoading.value = false;
      });
  };

  const handleChangeCapacity = (value: string) => {
    if (value === '') {
      modelValue.value.capacity = value;
      return;
    }

    const capacityValue = Number(value);
    const futureCapacityValue = Number(modelValue.value.future_capacity);

    if (modelValue.value.future_capacity === '') {
      modelValue.value.capacity = capacityValue;
    } else {
      modelValue.value.capacity = capacityValue > futureCapacityValue ? futureCapacityValue : capacityValue;
    }
  };

  const handleChangeFutureCapacity = (value: string) => {
    if (value === '') {
      modelValue.value.future_capacity = value;
      return;
    }

    const futureCapacityValue = Number(value);
    const capacityValue = Number(modelValue.value.capacity);

    if (modelValue.value.future_capacity === '') {
      modelValue.value.future_capacity = futureCapacityValue;
    } else {
      modelValue.value.future_capacity = capacityValue > futureCapacityValue ? capacityValue : futureCapacityValue;
    }
  };

  const fetchSpecResourceCount = _.debounce(() => {
    getSpecResourceCount({
      bk_biz_id: Number(props.bizId),
      bk_cloud_id: Number(props.cloudId),
      spec_ids: specs.value.map(item => item.spec_id),
    }).then((data) => {
      renderSpecs.value = specs.value.map(item => ({
        ...item,
        count: data[item.spec_id] ?? 0,
      }));
    });
  }, 100);

  watch(() => sliderProps.value, _.debounce(() => {
    modelValue.value.spec_id = '';
    if (sliderProps.value[1] > 0) {
      fetchFilterClusterSpec();
    } else {
      specs.value = [];
      renderSpecs.value = [];
    }
  }, 400), { immediate: true, deep: true });

  watch(() => modelValue.value.spec_id, () => {
    if (modelValue.value.spec_id) {
      specRef.value?.clearValidate();
    }
  });

  watch([
    () => props.bizId,
    () => props.cloudId,
    specs,
  ], () => {
    if (
      typeof props.bizId === 'number'
      && props.bizId > 0
      && typeof props.cloudId === 'number'
      && specs.value.length > 0
    ) {
      fetchSpecResourceCount();
    }
  }, { immediate: true, deep: true });

  watch([
    () => modelValue.value.capacity,
    () => modelValue.value.future_capacity,
  ], ([capacityValue, futureCapacityValue]) => {
    if (capacityValue === '' || futureCapacityValue === '') {
      resetSlider();
    } else {
      fetchQPSRange();
    }
  });

  const handleRowClick = (event: Event, row: ClusterSpecModel) => {
    modelValue.value.spec_id = row.spec_id;
  };

  const handleFocusCapacity = () => {
    sliderProps.disabled = true;
  };

  const handleBlurCapacity = () => {
    sliderProps.disabled = false;
  };

  defineExpose({
    getData() {
      if (applyType.value === 'auto') {
        const item = specs.value.find(item => item.spec_id === Number(modelValue.value.spec_id))!;
        return {
          spec_name: item.spec_name,
          machine_pair: item.machine_pair,
          cluster_shard_num: item.cluster_shard_num,
          cluster_capacity: item.cluster_capacity,
          qps: item.qps
        };
      }
      const item = specSelectorRef.value!.getData()!
      const { count } = modelValue.value
      return {
        spec_name: item.spec_name,
        machine_pair: count,
        cluster_shard_num: clusterShardNum.value,
        cluster_capacity: count * getSpecCapacity(item.storage_spec!),
        qps: item.qps
      };
    },
  });
</script>

<style lang="less" scoped>
  .redis-backend-spec {
    max-width: 1200px;
    padding: 24px 24px 24px 10px;
    background-color: #f5f7fa;
    border-radius: 2px;

    .input-desc {
      padding-left: 12px;
      font-size: 12px;
      line-height: 20px;
      color: #63656e;
    }

    :deep(.spec-radio) {
      max-width: 100%;
      overflow: hidden;

      .bk-radio-input {
        flex-shrink: 0;
      }

      .bk-radio-label {
        flex: 1;
        overflow: hidden;
      }
    }

    .custom-edit-table {
      :deep(.bk-table-body) {
        .cell {
          height: 42px !important;
        }

        tr:hover td {
          background-color: #f5f7fa !important;
        }
      }
    }
  }
</style>
