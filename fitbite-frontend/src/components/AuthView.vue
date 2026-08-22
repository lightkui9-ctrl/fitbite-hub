<template>
  <div class="auth-wrap">
    <el-card class="auth-card" shadow="always">
      <div class="brand">
        <el-icon class="brand-icon"><Food /></el-icon>
        <h2>FitBite 智膳</h2>
        <p class="sub">基于 AI Agent 的个性化减脂餐与健康管理系统</p>
      </div>

      <el-tabs v-model="mode" class="auth-tabs" stretch>
        <!-- 登录 -->
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-position="top"
            @submit.prevent
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                show-password
                placeholder="请输入密码"
                :prefix-icon="Lock"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-button type="primary" class="full" :loading="loading" @click="handleLogin">
              登录
            </el-button>
          </el-form>
        </el-tab-pane>

        <!-- 注册 -->
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="regFormRef"
            :model="regForm"
            :rules="regRules"
            label-position="top"
            @submit.prevent
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="regForm.username" placeholder="给自己起个用户名" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="regForm.password"
                type="password"
                show-password
                placeholder="至少 6 位"
                :prefix-icon="Lock"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="regForm.confirmPassword"
                type="password"
                show-password
                placeholder="请再次输入密码"
                :prefix-icon="Lock"
                @keyup.enter="handleRegister"
              />
            </el-form-item>
            <el-button type="primary" class="full" :loading="loading" @click="handleRegister">
              注册并登录
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { User, Lock, Food } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const mode = ref<'login' | 'register'>('login')
const loading = ref(false)

// ---- 登录表单 ----
const loginFormRef = ref<FormInstance>()
const loginForm = reactive({ username: '', password: '' })
const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// ---- 注册表单 ----
const regFormRef = ref<FormInstance>()
const regForm = reactive({ username: '', password: '', confirmPassword: '' })
const validateConfirm = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== regForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}
const regRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validateConfirm, trigger: 'blur' }]
}

async function handleLogin() {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.login(loginForm.username, loginForm.password)
      ElMessage.success('登录成功')
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.message || e?.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}

async function handleRegister() {
  if (!regFormRef.value) return
  await regFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.register({ ...regForm })
      ElMessage.success('注册成功，正在登录…')
      // 注册成功后使用同一凭据自动登录，直接进入系统
      await userStore.login(regForm.username, regForm.password)
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.message || e?.message || '注册失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-wrap {
  min-height: 100vh;
  display:flex;
  align-items:center;
  justify-content:center;
  background: linear-gradient(135deg, #ecfdf5, #f0fdfa);
}
.auth-card {
  width: 380px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,.08);
}
.brand { text-align:center; margin-bottom: 8px; }
.brand-icon { font-size: 36px; color: #10b981; }
.brand h2 { margin: 6px 0 2px; color: #0f172a; }
.sub { font-size: 12px; color: #94a3b8; margin: 0; }
.full { width: 100%; margin-top: 6px; }
</style>
