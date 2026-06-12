import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'
import router from '@/router'
import { useUserStore } from '@/stores/user'

interface ApiEnvelope<T> {
  code: number
  message: string
  data: T
}

export class ApiError extends Error {
  code?: number
  status?: number

  constructor(message: string, options?: { code?: number; status?: number }) {
    super(message)
    this.name = 'ApiError'
    this.code = options?.code
    this.status = options?.status
  }
}

const instance = axios.create({
  baseURL: '/api',
  timeout: 10000
})

instance.interceptors.request.use((config) => {
  const userStore = useUserStore()
  config.headers = config.headers ?? {}
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    const userStore = useUserStore()
    const status = error.response?.status as number | undefined
    const message = error.response?.data?.message || error.message || '请求失败'

    if (status === 401) {
      userStore.logout()
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }

    return Promise.reject(new ApiError(message, { status }))
  }
)

const unwrap = <T>(response: AxiosResponse<ApiEnvelope<T>>): T => {
  const payload = response.data
  if (payload.code !== 200) {
    if (payload.code === 401) {
      const userStore = useUserStore()
      userStore.logout()
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }
    throw new ApiError(payload.message, { code: payload.code, status: response.status })
  }
  return payload.data
}

const http = {
  get<T>(url: string, config?: AxiosRequestConfig) {
    return instance.get<ApiEnvelope<T>>(url, config).then(unwrap)
  },
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return instance.post<ApiEnvelope<T>>(url, data, config).then(unwrap)
  },
  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return instance.put<ApiEnvelope<T>>(url, data, config).then(unwrap)
  },
  delete<T>(url: string, config?: AxiosRequestConfig) {
    return instance.delete<ApiEnvelope<T>>(url, config).then(unwrap)
  }
}

export default http
