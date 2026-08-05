import axios from 'axios'

const TOKEN_KEY = 'shortify_access_token'
const AUTH_CHANGE_EVENT = 'shortify_auth_changed'

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  withCredentials: true,   // send cookies (guest_id) on every request
  headers: {
    'Content-Type': 'application/json',
  },
})

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function isAuthenticated() {
  return Boolean(getAuthToken())
}

function notifyAuthChange(token) {
  window.dispatchEvent(new CustomEvent(AUTH_CHANGE_EVENT, { detail: { token } }))
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

  notifyAuthChange(token)
}

export function clearAuthToken() {
  setAuthToken(null)
}

export function subscribeToAuthChanges(listener) {
  const handler = (event) => listener(event.detail?.token ?? null)
  window.addEventListener(AUTH_CHANGE_EVENT, handler)
  return () => window.removeEventListener(AUTH_CHANGE_EVENT, handler)
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
