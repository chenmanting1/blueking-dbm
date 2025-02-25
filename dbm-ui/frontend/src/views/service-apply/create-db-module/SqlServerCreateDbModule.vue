<template>
  <SmartAction :offset-target="getSmartActionOffsetTarget">
    <DbForm
      ref="createModuleFormRef"
      class="create-module db-scroll-y"
      :label-width="180"
      :model="formData">
      <DbCard
        class="mb-16"
        :title="t('模块信息')">
        <BkFormItem
          :label="t('模块名称')"
          property="module_name"
          required
          :rules="rules.module_name">
          <BkInput
            v-model="formData.module_name"
            :placeholder="t('由英文字母_数字_连字符_组成')" />
          <span class="belong-business ml-16"> {{ t('所属业务') }} : {{ bizInfo.name }} </span>
        </BkFormItem>
      </DbCard>
      <DbCard
        class="mb-16"
        :title="t('绑定数据库配置')">
        <BkFormItem
          :label="t('数据库类型')"
          property="mysql_type">
          <BkTag
            class="mysql-type-item"
            theme="info"
            type="stroke">
            <template #icon>
              <DbIcon
                class="mr-4"
                type="sqlserver" />
            </template>
            {{ ticketInfo.name }}
          </BkTag>
        </BkFormItem>
        <BkFormItem
          :label="t('数据库版本')"
          property="version"
          required>
          <DeployVersion
            v-model="formData.version"
            db-type="sqlserver"
            :placeholder="t('请选择数据库版本')"
            query-key="sqlserver" />
        </BkFormItem>
        <BkFormItem
          :label="t('字符集')"
          property="character_set"
          required>
          <BkSelect
            v-model="formData.character_set"
            :clearable="false"
            filterable
            :placeholder="t('请选择字符集')">
            <BkOption
              v-for="(item, index) in characterSets"
              :key="index"
              :label="item"
              :value="item" />
          </BkSelect>
        </BkFormItem>
        <BkFormItem
          :label="t('数据库配置')"
          property="version"
          required>
          <BkSelect
            v-model="formData.version"
            :clearable="false"
            disabled
            :placeholder="t('请选择数据库版本')">
            <BkOption
              v-for="(item, index) in characterSets"
              :key="index"
              :label="item"
              :value="item" />
          </BkSelect>
        </BkFormItem>
        <BkFormItem
          :label="t('操作系统版本')"
          property="operatingSystemVersion"
          required>
          <BkSelect
            v-model="formData.operatingSystemVersion"
            filterable
            multiple
            :placeholder="t('请选择操作系统版本')">
            <BkOption
              v-for="item in operatingSystemVersionList"
              :key="item"
              :label="item"
              :value="item" />
          </BkSelect>
        </BkFormItem>
        <BkFormItem
          :label="t('实例内存分配比率 (50~80%)')"
          property="memoryAllocationRatio"
          required>
          <div class="input-box">
            <BkInput
              v-model="formData.memoryAllocationRatio"
              class="item-input num-input"
              :max="80"
              :min="50"
              :placeholder="t('请输入')"
              type="number" />
            <div class="uint-text">%</div>
          </div>
        </BkFormItem>
        <BkFormItem
          :label="t('最大系统保留内存')"
          property="maxSystemReservedMemory"
          required>
          <div class="input-box">
            <BkInput
              v-model="formData.maxSystemReservedMemory"
              class="item-input num-input"
              disabled
              :min="1"
              :placeholder="t('请输入')"
              type="number" />
            <div class="uint-text">GB</div>
          </div>
        </BkFormItem>
        <BkFormItem
          :label="t('主从方式')"
          property="haMode"
          required>
          <BkRadioGroup
            v-model="formData.haMode"
            disabled>
            <BkRadio
              v-for="item in haModeList"
              :key="item.value"
              :label="item.value">
              {{ item.label }}
            </BkRadio>
          </BkRadioGroup>
        </BkFormItem>
      </DbCard>
      <!-- <DbCard :title="t('参数配置')">
        <BkLoading :loading="parameterTableLoading">
          <ParameterTable
            ref="parameterTableRef"
            :data="leaveConfigData?.conf_items"
            :is-anomalies="parameterTableLoading"
            level="module"
            @refresh="fetchLevelConfig" />
        </BkLoading>
      </DbCard> -->
    </DbForm>
    <template #action>
      <BkButton
        class="w-88 mt-8"
        :loading="isLoading"
        theme="primary"
        @click="handleSubmit">
        {{ t('确定') }}
      </BkButton>
      <BkButton
        class="w-88 ml-8 mt-8"
        :disabled="isLoading"
        @click="resetFormData()">
        {{ t('重置') }}
      </BkButton>
    </template>
  </SmartAction>
</template>

<script setup lang="ts">
  import InfoBox from 'bkui-vue/lib/info-box';
  import { useI18n } from 'vue-i18n';
  import { useRequest } from 'vue-request';

  import { createModules } from '@services/source/cmdb';
  import {
    // getLevelConfig,
    saveModulesDeployInfo,
  } from '@services/source/configs';
  import { listSqlserverSystemVersion } from '@services/source/version'

  import { useGlobalBizs } from '@stores';

  import {
    sqlServerType,
    type SqlServerTypeString,
  } from '@common/const';

  import DeployVersion from '@components/apply-items/DeployVersion.vue';

  // import ParameterTable from '@views/db-configure/components/ParameterTable.vue';
  import { messageSuccess } from '@utils';

  const { t } = useI18n();
  const router = useRouter();
  const route = useRoute();

  const {
    bizs,
    currentBizId,
  } = useGlobalBizs();

  const haModeList = [
    {
      value: 'mirroring',
      label: t('镜像'),
    },
    {
      value: 'always_on',
      label: 'always on',
    },
  ];

  const characterSets = ['Chinese_PRC_CI_AS', 'Latin1_General_100_CI_AS'];
  const bizInfo = bizs.find(info => info.bk_biz_id === currentBizId) || { name: '' };
  const paramBizId = Number(route.params.bk_biz_id);

  const rules = {
    module_name: [
      {
        required: true,
        message: t('模块名称不能为空'),
        trigger: 'blur',
      },
      {
        pattern: /^[0-9a-zA-Z-]+$/,
        message: t('由英文字母_数字_连字符_组成'),
        trigger: 'blur',
      },
    ],
  };

  /**
   * 获取表单基础信息
   */
  const getFormData = () => ({
    module_name: '',
    sqlserver_type: route.params.type,
    version: '',
    camelCase: '', // 数据库配置
    character_set: '', // 字符集
    memoryAllocationRatio: '', // 内存分配比
    maxSystemReservedMemory: 32, // 最大系统保留内存
    operatingSystemVersion: [] as string[], // 操作系统版本
    haMode: '', // 主从方式
  });

  const createModuleFormRef = ref();

  const formData = reactive(getFormData());

  const ticketInfo = computed(() => sqlServerType[route.params.type as SqlServerTypeString]);

  const {
    loading: isLoading,
    run: runCreateModules,
  } = useRequest(createModules, {
    manual: true,
    onSuccess(res) {
      if (res.db_module_id) {
        // 绑定数据库配置
        runSaveModuleDeploy({
          level_name: 'module',
          version: 'deploy_info',
          conf_type: 'deploy',
          bk_biz_id: paramBizId,
          level_value: res.db_module_id, // 创建模块后的 db_module_id
          meta_cluster_type: String(route.query.cluster_type),
          conf_items: [
            {
              conf_name: "charset",
              conf_value: formData.character_set,
              op_type: "update",
              description: t("字符集")
            },
            {
              conf_name: "db_version",
              conf_value: formData.version,
              op_type: "update",
              description: t("数据库版本")
            },
            {
              conf_name: "buffer_percent",
              conf_value: formData.memoryAllocationRatio,
              op_type: "update",
              description: t("实际内存分配比率")
            },
            {
              conf_name: "max_remain_mem_gb",
              conf_value: String(formData.maxSystemReservedMemory),
              op_type: "update",
              description: t("最大系统保留内存")
            },
            {
              conf_name: "sync_type",
              conf_value: formData.haMode,
              op_type: "update",
              description: t("主从方式")
            },
            {
              conf_name: "system_version",
              conf_value: formData.operatingSystemVersion.map(versionItem => versionItem.replace(/\s*/g, '')).join(','),
              op_type: "update",
              description: t("操作系统版本")
            }
          ]
        });
      }
    },
  });

  // const {
  //   loading: parameterTableLoading,
  //   run: runGetLevelConfig,
  //   data: leaveConfigData,
  // } = useRequest(getLevelConfig, {
  //   manual: true,
  // });

  const { run: runSaveModuleDeploy } = useRequest(saveModulesDeployInfo, {
    manual: true,
    onSuccess() {
      messageSuccess(t('创建DB模块并绑定数据库配置成功'));
      window.changeConfirm = false;
    }
  });

  const {
    data: operatingSystemVersionList,
    run: listSqlserverSystemVersionRun
  } = useRequest(listSqlserverSystemVersion, {
    manual:true
  });

  watch(() => formData.version, (version) => {
    if (version) {
      // fetchLevelConfig();

      formData.operatingSystemVersion = [] as string[]
      listSqlserverSystemVersionRun({
        sqlserver_version: version
      })

      if (Number(version.slice(-4)) > 2017) {
        formData.haMode = 'always_on';
      } else {
        formData.haMode = 'mirroring';
      }
    }
  }, { immediate: true });

  const getSmartActionOffsetTarget = () => document.querySelector('.bk-form-content');

  // const fetchLevelConfig = () => {
  //   runGetLevelConfig({
  //     bk_biz_id: paramBizId,
  //     level_name: 'module',
  //     level_value: Number(route.query.db_module_id),
  //     meta_cluster_type: String(route.query.cluster_type),
  //     conf_type: 'dbconf',
  //     version: formData.version,
  //   });
  // };

  /**
   * 提交表单
   */
  const handleSubmit = async () => {
    // 校验表单信息
    await createModuleFormRef.value.validate();
    // 创建模块
    runCreateModules({
      db_module_name: formData.module_name,
      cluster_type: String(route.query.cluster_type),
      id: paramBizId,
    });
  };

  /**
   * 重置表单
   */
  const resetFormData = () => {
    InfoBox({
      title: t('确认重置表单内容'),
      content: t('重置后_将会清空当前填写的内容'),
      cancelText: t('取消'),
      onConfirm: () => {
        Object.assign(formData, getFormData());
        nextTick(() => {
          window.changeConfirm = false;
        });
        return true;
      },
    });
  };

  defineExpose({
    routerBack() {
      if (!route.query.from) {
        router.push({
          name: 'serviceApply',
        });
        return;
      }
      router.push({
        name: String(route.query.from),
      });
    },
  });
</script>

<style lang="less" scoped>
  @import '@styles/mixins';

  .create-module {
    .bk-form-content .bk-input,
    .bk-select {
      width: 435px;
    }

    .input-box {
      display: flex;
      width: 100%;
      align-items: center;

      .num-input {
        height: 32px;
      }

      .uint-text {
        margin-left: 12px;
        font-size: 12px;
        color: #63656e;
      }
    }
  }
</style>
