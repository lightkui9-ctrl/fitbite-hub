import { api } from './diet'

// 用户注册（含二次确认密码）
export function register(data: {
  username: string
  password: string
  confirmPassword: string
}) {
  return api.post('/user/register', data)
}

// 用户登录
export function login(username: string, password: string) {
  return api.post('/user/login', { username, password })
}

// 获取当前登录用户信息（需携带 Token）
export function getMe() {
  return api.get('/user/me')
}

// 保存 / 更新个人档案（性别 / 年龄 / 身高 / 体重 / 目标体重 / 活动量）
export function saveProfile(data: {
  username: string
  gender?: string
  age?: number
  height?: number
  weight?: number
  targetWeight?: number
  activityLevel?: string
}) {
  return api.post('/user/save', data)
}
