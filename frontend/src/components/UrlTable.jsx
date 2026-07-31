import { Link } from 'react-router-dom'
import { useState } from 'react'
import { useToast } from './Toast'

/**
 * UrlTable — displays a list of shortened URLs in a responsive table.
 * Props:
 *   urls:      array of URL objects from the API
 *   onDelete:  (id: number) => void
 *   loading:   boolean
 */
export default function UrlTable({ urls = [], onDelete, loading = false }) {
  const { addToast } = useToast()
  const [confirmId, setConfirmId] = useState(null)
  const [copiedId, setCopiedId] = useState(null)

  async function handleCopy(shortUrl, id) {
    try {
      await navigator.clipboard.writeText(shortUrl)
    } catch {
      const el = document.createElement('input')
      el.value = shortUrl
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
    }
    setCopiedId(id)
    addToast('Link copied to clipboard!', 'success')
    setTimeout(() => setCopiedId(null), 2000)
  }

  async function handleDelete(id, shortCode) {
    setConfirmId(null)
    const ok = await onDelete(id)
    if (ok !== false) {
      addToast(`"${shortCode}" deleted.`, 'info')
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-3" role="status" aria-label="Loading URLs">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-12 bg-gray-200 rounded-lg" />
        ))}
      </div>
    )
  }

  if (urls.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400">
        <p className="text-4xl mb-3">🔗</p>
        <p className="text-sm">No links yet. Create your first short URL above!</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-gray-600">Original URL</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-600">Short link</th>
            <th className="px-4 py-3 text-center font-semibold text-gray-600">Clicks</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-600">Created</th>
            <th className="px-4 py-3 text-right font-semibold text-gray-600">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-100">
          {urls.map((url) => (
            <tr key={url.id} className="hover:bg-gray-50 transition-colors">
              {/* Original URL */}
              <td className="px-4 py-3 max-w-xs">
                <a
                  href={url.original_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={url.original_url}
                  className="text-gray-700 hover:text-blue-600 truncate block max-w-[220px]
                    transition-colors"
                >
                  {url.original_url}
                </a>
              </td>

              {/* Short link */}
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <a
                    href={url.short_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline font-medium"
                  >
                    {url.short_code}
                  </a>
                  <button
                    onClick={() => handleCopy(url.short_url, url.id)}
                    className="text-gray-400 hover:text-blue-600 transition-colors"
                    aria-label={`Copy ${url.short_url}`}
                    title="Copy short link"
                  >
                    {copiedId === url.id ? (
                      <span className="text-xs text-green-600 font-medium">✓</span>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
                        viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round"
                          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2
                             m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2
                             2v8a2 2 0 002 2z" />
                      </svg>
                    )}
                  </button>
                </div>
              </td>

              {/* Clicks */}
              <td className="px-4 py-3 text-center">
                <Link
                  to={`/analytics/${url.id}`}
                  className="inline-flex items-center gap-1 text-gray-600
                    hover:text-blue-600 transition-colors"
                  title="View analytics"
                >
                  <span className="font-semibold">{url.click_count}</span>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none"
                    viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round"
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002
                         2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10
                         m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2
                         a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </Link>
              </td>

              {/* Created date */}
              <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                {new Date(url.created_at).toLocaleDateString(undefined, {
                  month: 'short', day: 'numeric', year: 'numeric',
                })}
              </td>

              {/* Actions */}
              <td className="px-4 py-3 text-right">
                {confirmId === url.id ? (
                  <span className="inline-flex items-center gap-2">
                    <span className="text-xs text-gray-500">Delete?</span>
                    <button
                      onClick={() => { handleDelete(url.id, url.short_code); setConfirmId(null) }}
                      className="text-xs px-2 py-1 bg-red-600 text-white rounded
                        hover:bg-red-700 transition-colors"
                    >
                      Yes
                    </button>
                    <button
                      onClick={() => setConfirmId(null)}
                      className="text-xs px-2 py-1 border border-gray-300 rounded
                        hover:bg-gray-100 transition-colors"
                    >
                      No
                    </button>
                  </span>
                ) : (
                  <button
                    onClick={() => setConfirmId(url.id)}
                    className="text-gray-400 hover:text-red-600 transition-colors"
                    aria-label={`Delete URL ${url.short_code}`}
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
                      viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0
                           01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0
                           00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
