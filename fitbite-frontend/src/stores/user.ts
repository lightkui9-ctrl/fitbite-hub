import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getMe, saveProfile } from '../api/auth'

const TOKEN_KEY = 'fitbite_token'
const USER_KEY = 'fitbite_user'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref<any>(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  function persist(t: string, u: any) {
    token.value = t
    user.value = u
    localStorage.setItem(TOKEN_KEY, t)
    localStorage.setItem(USER_KEY, JSON.stringify(u))
  }

  async function login(username: string, password: string) {
    const res = await loginApi(username, password)
    const { token: tk, user: u } = res.data
    persist(tk, u)
    return u
  }

  async function register(payload: { username: string; password: string; confirmPassword: string }) {
    const res = await registerApi(payload)
    return res.data
  }

  async function fetchMe() {
    const res = await getMe()
    user.value = res.data
    localStorage.setItem(USER_KEY, JSON.stringify(res.data))
    return res.data
  }

  async function updateProfile(data: any) {
    const res = await saveProfile({ username: user.value?.username, ...data })
    user.value = res.data
    localStorage.setItem(USER_KEY, JSON.stringify(res.data))
    return res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return { token, user, isLoggedIn, login, register, fetchMe, updateProfile, logout }
})
