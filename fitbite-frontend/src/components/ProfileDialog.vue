<template>
  <el-dialog v-model="visible" title="完善个人档案" width="440px" @open="syncForm">
    <el-form :model="form" label-width="90px">
      <el-form-item label="性别">
        <el-select v-model="form.gender" placeholder="请选择" style="width:100%">
          <el-option label="男" value="male" />
          <el-option label="女" value="female" />
        </el-select>
      </el-form-item>
      <el-form-item label="年龄">
        <el-input-number v-model="form.age" :min="1" :max="120" />
      </el-form-item>
      <el-form-item label="身高 (cm)">
        <el-input-number v-model="form.height" :min="50" :max="250" :step="0.5" />
      </el-form-item>
      <el-form-item label="当前体重 (kg)">
        <el-input-number v-model="form.weight" :min="20" :max="300" :step="0.5" />
      </el-form-item>
      <el-form-item label="目标体重 (kg)">
        <el-input-number v-model="form.targetWeight" :min="20" :max="300" :step="0.5" />
      </el-form-item>
      <el-form-item label="日常活动量">
        <el-select v-model="form.activityLevel" placeholder="请选择" style="width:100%">
          <el-option label="久坐" value="sedentary" />
          <el-option label="轻度活动" value="light" />
          <el-option label="中度活动" value="moderate" />
          <el-option label="高度活动" value="active" />
          <el-option label="极高活动" value="very_active" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [boolean] }>()
const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const userStore = useUserStore()
const loading = ref(false)
const form = ref({
  gender: '',
  age: undefined as number | undefined,
  height: undefined as number | undefined,
  weight: undefined as number | undefined,
  targetWeight: undefined as number | undefined,
  activityLevel: ''
})

function syncForm() {
  const u = userStore.user || {}
  form.value = {
    gender: u.gender || '',
    age: u.age,
    height: u.height,
    weight: u.weight,
    targetWeight: u.targetWeight,
    activityLevel: u.activityLevel || ''
  }
}

async function handleSave() {
  loading.value = true
  try {
    await userStore.updateProfile({ ...form.value })
    ElMessage.success('档案已保存')
    visible.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally {
    loading.value = false
  }
}
</script>
