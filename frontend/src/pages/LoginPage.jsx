import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import axiosClient, { setAuthToken } from '../api/axiosClient'
import { useToast } from '../components/Toast'

export default function LoginPage() {
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const token = localStorage.getItem('shortify_access_token')
  if (token) {
    return <Navigate to="/dashboard" replace />
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { data } = await axiosClient.post('/api/auth/login', {
        identifier,
        password,
      })

      setAuthToken(data.access_token)
      addToast('Logged in successfully.', 'success')
      navigate('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md bg-white border border-gray-200 rounded-2xl shadow-sm p-8">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Login</h1>
          <p className="text-sm text-gray-500 mt-1">Access your dashboard and links.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div>
            <label htmlFor="identifier" className="block text-sm font-medium text-gray-700 mb-1">
              Email or username
            </label>
            <input
              id="identifier"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className="px-3 py-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-6 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-60"
          >
            {loading ? 'Signing in…' : 'Login'}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-500">
          New here?{' '}
          <Link to="/register" className="font-medium text-blue-600 hover:underline">
            Create an account
          </Link>
        </p>
      </div>
    </main>
  )
}
