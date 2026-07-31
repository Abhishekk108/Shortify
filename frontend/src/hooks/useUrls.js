import { useState, useEffect, useCallback } from 'react'
import axiosClient from '../api/axiosClient'

/**
 * Custom hook to fetch and manage the URL list.
 * Supports search, pagination, and delete.
 */
export default function useUrls({ search = '', skip = 0, limit = 20 } = {}) {
  const [urls, setUrls] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchUrls = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { skip, limit }
      if (search) params.search = search
      const { data } = await axiosClient.get('/api/urls', { params })
      setUrls(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'Failed to load URLs.')
    } finally {
      setLoading(false)
    }
  }, [search, skip, limit])

  useEffect(() => {
    fetchUrls()
  }, [fetchUrls])

  const deleteUrl = useCallback(async (id) => {
    try {
      await axiosClient.delete(`/api/urls/${id}`)
      setUrls((prev) => prev.filter((u) => u.id !== id))
      setTotal((prev) => prev - 1)
      return true
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'Failed to delete URL.')
      return false
    }
  }, [])

  return { urls, total, loading, error, refetch: fetchUrls, deleteUrl }
}
