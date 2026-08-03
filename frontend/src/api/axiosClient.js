import axios from 'axios'

const TOKEN_KEY = 'shortify_access_token'

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }

  if (token) {
    axiosClient.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete axiosClient.defaults.headers.common.Authorization
  }
}

export function clearAuthToken() {
  setAuthToken(null)
}

const persistedToken = getAuthToken()
if (persistedToken) {
  setAuthToken(persistedToken)
}

axiosClient.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default axiosClient
