import { useState } from 'react'
import axiosClient from '../api/axiosClient'
import { useToast } from './Toast'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

/** Basic client-side URL validation */
function isValidUrl(str) {
  try {
    const u = new URL(str.trim())
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

/**
 * ShortenForm — lets users paste a long URL and optional alias,
 * submits to POST /api/urls, then shows the generated short link.
 *
 * Props:
 *   onCreated: (urlObj) => void   called after a successful creation
 */
export default function ShortenForm({ onCreated }) {
  const { addToast } = useToast()
  const [longUrl, setLongUrl] = useState('')
  const [alias, setAlias] = useState('')
  const [result, setResult] = useState(null)   // created URL object
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState(null)

  // ── Validation ────────────────────────────────────────────────────────────
  function validate() {
    const errs = {}

    if (!longUrl.trim()) {
      errs.longUrl = 'Please enter a URL.'
    } else if (!isValidUrl(longUrl)) {
      errs.longUrl = 'Please enter a valid http:// or https:// URL.'
    }

    if (alias.trim()) {
      if (alias.trim().length < 3) {
        errs.alias = 'Alias must be at least 3 characters.'
      } else if (alias.trim().length > 50) {
        errs.alias = 'Alias must be 50 characters or fewer.'
      } else if (!/^[a-zA-Z0-9-]+$/.test(alias.trim())) {
        errs.alias = 'Alias may only contain letters, digits, and hyphens.'
      }
    }

    return errs
  }

  // ── Submit ────────────────────────────────────────────────────────────────
  async function handleSubmit(e) {
    e.preventDefault()
    setApiError(null)
    setResult(null)

    const errs = validate()
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    const payload = { original_url: longUrl.trim() }
    if (alias.trim()) payload.custom_alias = alias.trim()

    setLoading(true)
    try {
      const { data } = await axiosClient.post('/api/urls', payload)
      setResult(data)
      setLongUrl('')
      setAlias('')
      setErrors({})
      addToast('Short link created!', 'success')
      if (onCreated) onCreated(data)
    } catch (err) {
      const detail = err?.response?.data?.detail
      if (typeof detail === 'string') {
        setApiError(detail)
      } else if (Array.isArray(detail)) {
        // Pydantic validation error array
        setApiError(detail.map((d) => d.msg).join(', '))
      } else {
        setApiError('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  // ── Copy to clipboard ─────────────────────────────────────────────────────
  async function handleCopy() {
    if (!result?.short_url) return
    try {
      await navigator.clipboard.writeText(result.short_url)
    } catch {
      // fallback for browsers without clipboard API
      const el = document.createElement('input')
      el.value = result.short_url
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
    }
    setCopied(true)
    addToast('Link copied to clipboard!', 'success')
    setTimeout(() => setCopied(false), 2000)
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} noValidate aria-label="URL shortener form">
        {/* Long URL field */}
        <div className="mb-3">
          <label htmlFor="longUrl" className="block text-sm font-medium text-gray-700 mb-1">
            Long URL <span className="text-red-500">*</span>
          </label>
          <input
            id="longUrl"
            type="url"
            value={longUrl}
            onChange={(e) => setLongUrl(e.target.value)}
            placeholder="https://example.com/very/long/path"
            className={`w-full px-4 py-2.5 border rounded-lg text-sm focus:outline-none
              focus:ring-2 focus:ring-blue-500 focus:border-transparent
              ${errors.longUrl ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-white'}`}
            aria-invalid={!!errors.longUrl}
            aria-describedby={errors.longUrl ? 'longUrl-error' : undefined}
            disabled={loading}
          />
          {errors.longUrl && (
            <p id="longUrl-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.longUrl}
            </p>
          )}
        </div>

        {/* Custom alias field */}
        <div className="mb-4">
          <label htmlFor="alias" className="block text-sm font-medium text-gray-700 mb-1">
            Custom alias{' '}
            <span className="text-gray-400 font-normal">(optional)</span>
          </label>
          <div className="flex items-center gap-1.5">
            <span className="text-sm text-gray-400 shrink-0">{BASE_URL}/</span>
            <input
              id="alias"
              type="text"
              value={alias}
              onChange={(e) => setAlias(e.target.value)}
              placeholder="my-link"
              maxLength={50}
              className={`flex-1 px-4 py-2.5 border rounded-lg text-sm focus:outline-none
                focus:ring-2 focus:ring-blue-500 focus:border-transparent
                ${errors.alias ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-white'}`}
              aria-invalid={!!errors.alias}
              aria-describedby={errors.alias ? 'alias-error' : undefined}
              disabled={loading}
            />
          </div>
          {errors.alias && (
            <p id="alias-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.alias}
            </p>
          )}
        </div>

        {/* API error */}
        {apiError && (
          <div role="alert" className="mb-4 px-4 py-3 bg-red-50 border border-red-200
            rounded-lg text-sm text-red-700">
            {apiError}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-6 bg-blue-600 text-white text-sm font-semibold
            rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors
            disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? 'Shortening…' : 'Shorten URL'}
        </button>
      </form>

      {/* Result card */}
      {result && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg"
          role="status" aria-live="polite">
          <p className="flex items-center gap-1.5 text-xs text-green-600 font-medium mb-2 uppercase tracking-wide">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none"
              viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5} aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            Short link created
          </p>
          <div className="flex items-center gap-2">
            <a
              href={result.short_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 text-sm font-medium text-blue-700 underline truncate
                hover:text-blue-900 transition-colors"
            >
              {result.short_url}
            </a>
            <button
              onClick={handleCopy}
              className="shrink-0 px-3 py-1.5 text-xs font-medium border rounded-md
                transition-colors
                bg-white border-gray-300 text-gray-700 hover:bg-gray-50
                active:bg-gray-100"
              aria-label="Copy short link to clipboard"
            >
              {copied ? (
                <span className="flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none"
                    viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  Copied!
                </span>
              ) : 'Copy'}
            </button>
          </div>
          <p className="mt-2 text-xs text-gray-500 truncate">
            → {result.original_url}
          </p>
        </div>
      )}
    </div>
  )
}
