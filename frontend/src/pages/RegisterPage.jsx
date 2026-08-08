import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import axiosClient, { setAuthToken } from '../api/axiosClient'
import { useToast } from '../components/Toast'

function formatValidationError(detail) {
  if (Array.isArray(detail)) {
    const messages = detail.map((issue) => {
      const location = Array.isArray(issue?.loc) ? issue.loc.slice(1).join(' / ') : ''
      const message = issue?.msg ?? 'Invalid value'
      return location ? `${location}: ${message}` : message
    })

    return messages.join(' ')
  }

  if (typeof detail === 'string') {
    return detail
  }

  if (detail && typeof detail === 'object') {
    if (typeof detail.message === 'string') {
      return detail.message
    }

    if (Array.isArray(detail.errors)) {
      return detail.errors.map((issue) => issue?.msg ?? 'Invalid value').join(' ')
    }
  }

  return 'Validation failed. Please check the required fields.'
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
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
      const registerResponse = await axiosClient.post('/api/auth/register', {
        username,
        email,
        password,
      })

      if (registerResponse?.status !== 201) {
        throw new Error(`Unexpected registration status: ${registerResponse?.status ?? 'unknown'}`)
      }

      const { data } = await axiosClient.post('/api/auth/login', {
        identifier: email,
        password,
      })

      setAuthToken(data.access_token)
      addToast('Account created and logged in.', 'success')
      navigate('/dashboard')
    } catch (err) {
      const status = err?.response?.status
      const detail = err?.response?.data?.detail

      if (status === 422) {
        setError(`Validation error: ${formatValidationError(detail)}`)
      } else if (status === 409) {
        setError('username/email already exists. Please choose another username or email.')
      } else if (typeof detail === 'string') {
        setError(detail)
      } else if (err?.message) {
        setError(err.message)
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md bg-white border border-gray-200 rounded-2xl shadow-sm p-8">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Create account</h1>
          <p className="text-sm text-gray-500 mt-1">Start shortening and tracking your links.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="yourname"
              required
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
            {loading ? 'Creating account…' : 'Register'}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-500">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-blue-600 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  )
}
