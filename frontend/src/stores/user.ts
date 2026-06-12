import { defineStore } from 'pinia'
import http from '@/api/http'

export interface UserInfo {
  id: number
  username: string
  nickname: string
  role: string
  email: string
  phone: string
  avatar?: string
  gender?: string
  age?: number
  profile?: string
}

interface LoginResponse {
  token: string
  user: UserInfo
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null') as UserInfo | null
    }),
  actions: {
    async login(payload: { username: string; password: string }) {
      const res = await http.post<LoginResponse>('/auth/login', payload)
      this.token = res.token
      this.user = res.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    async fetchProfile() {
      this.user = await http.get<UserInfo>('/users/me')
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
