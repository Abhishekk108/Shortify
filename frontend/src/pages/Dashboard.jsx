import { useState, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import useUrls from '../hooks/useUrls'
import UrlTable from '../components/UrlTable'
import SearchBar from '../components/SearchBar'
import ShortenForm from '../components/ShortenForm'

const PAGE_SIZE = 20

export default function Dashboard() {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [page, setPage] = useState(0)           // 0-indexed page
  const [showForm, setShowForm] = useState(false)
  const debounceTimer = useRef(null)

  // Debounce search input — only fires query after 350 ms of no typing
  function handleSearchChange(value) {
    setSearch(value)
    setPage(0)
    clearTimeout(debounceTimer.current)
    debounceTimer.current = setTimeout(() => {
      setDebouncedSearch(value)
    }, 350)
  }

  const skip = page * PAGE_SIZE

  const { urls, total, loading, error, refetch, deleteUrl } = useUrls({
    search: debouncedSearch,
    skip,
    limit: PAGE_SIZE,
  })

  const totalPages = Math.ceil(total / PAGE_SIZE)

  // Called when ShortenForm creates a new link — refresh the list
  const handleCreated = useCallback(() => {
    setPage(0)
    setSearch('')
    setDebouncedSearch('')
    setShowForm(false)
    refetch()
  }, [refetch])

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-10">

        {/* ── Header ─────────────────────────────────────────────────────── */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              {total > 0
                ? `${total} link${total === 1 ? '' : 's'} total`
                : 'No links yet'}
            </p>
          </div>
          <button
            onClick={() => setShowForm((v) => !v)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white
              text-sm font-semibold rounded-lg hover:bg-blue-700 active:bg-blue-800
              transition-colors"
            aria-expanded={showForm}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
              viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d={showForm ? 'M20 12H4' : 'M12 4v16m8-8H4'} />
            </svg>
            {showForm ? 'Cancel' : 'New link'}
          </button>
        </div>

        {/* ── Inline shorten form ─────────────────────────────────────────── */}
        {showForm && (
          <div className="mb-8 bg-white border border-gray-200 rounded-xl shadow-sm p-6">
            <h2 className="text-base font-semibold text-gray-700 mb-4">
              Create a new short link
            </h2>
            <ShortenForm onCreated={handleCreated} />
          </div>
        )}

        {/* ── Summary stats bar ───────────────────────────────────────────── */}
        <SummaryBar />

        {/* ── Toolbar: search ─────────────────────────────────────────────── */}
        <div className="flex items-center justify-between mt-6 mb-4 gap-4 flex-wrap">
          <SearchBar
            value={search}
            onChange={handleSearchChange}
            placeholder="Search by URL or alias…"
          />
          {debouncedSearch && (
            <p className="text-sm text-gray-500">
              {total} result{total !== 1 ? 's' : ''} for{' '}
              <span className="font-medium text-gray-700">"{debouncedSearch}"</span>
            </p>
          )}
        </div>

        {/* ── Error banner ─────────────────────────────────────────────────── */}
        {error && (
          <div role="alert"
            className="mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg
              text-sm text-red-700 flex items-center justify-between">
            <span>{error}</span>
            <button onClick={refetch}
              className="ml-4 text-xs underline hover:no-underline">
              Retry
            </button>
          </div>
        )}

        {/* ── URL table ────────────────────────────────────────────────────── */}
        <UrlTable
          urls={urls}
          onDelete={deleteUrl}
          loading={loading}
        />

        {/* ── Pagination ───────────────────────────────────────────────────── */}
        {totalPages > 1 && (
          <Pagination
            page={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        )}
      </div>
    </main>
  )
}

/* ─── Summary stats bar ──────────────────────────────────────────────────── */
import { useEffect, useState as useStateLocal } from 'react'
import axiosClient from '../api/axiosClient'

function SummaryBar() {
  const [summary, setSummary] = useStateLocal(null)
  const [summaryLoading, setSummaryLoading] = useStateLocal(true)

  useEffect(() => {
    axiosClient.get('/api/analytics/summary')
      .then(({ data }) => setSummary(data))
      .catch(() => setSummary(null))
      .finally(() => setSummaryLoading(false))
  }, [])

  if (summaryLoading) {
    return (
      <div className="grid grid-cols-3 gap-4 animate-pulse">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-20 bg-gray-200 rounded-xl" />
        ))}
      </div>
    )
  }

  if (!summary) return null

  const stats = [
    {
      label: 'Total links',
      value: summary.total_links,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-500" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101
               m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      ),
    },
    {
      label: 'Total clicks',
      value: summary.total_clicks,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-500" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5" />
        </svg>
      ),
    },
    {
      label: 'Top link',
      value: summary.top_urls?.[0]?.short_code ?? '—',
      sub: summary.top_urls?.[0] ? `${summary.top_urls[0].click_count} clicks` : null,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-500" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0
               0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0
               0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      href: summary.top_urls?.[0] ? `/analytics/${summary.top_urls[0].id}` : null,
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {stats.map(({ label, value, sub, icon, href }) => (
        <div key={label}
          className="bg-white border border-gray-200 rounded-xl px-5 py-4 shadow-sm">
          <p className="flex items-center gap-1.5 text-xs text-gray-500 font-medium
            uppercase tracking-wide mb-1">
            {icon}
            {label}
          </p>
          {href ? (
            <Link to={href} className="text-2xl font-bold text-blue-600 hover:underline">
              {value}
            </Link>
          ) : (
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          )}
          {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
        </div>
      ))}
    </div>
  )
}

/* ─── Pagination ─────────────────────────────────────────────────────────── */
function Pagination({ page, totalPages, onPageChange }) {
  return (
    <nav
      className="mt-6 flex items-center justify-center gap-2"
      aria-label="Pagination"
    >
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page === 0}
        className="px-3 py-1.5 text-sm border rounded-md text-gray-600
          hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed
          transition-colors"
        aria-label="Previous page"
      >
        ← Prev
      </button>

      {/* Page number pills */}
      {[...Array(totalPages)].map((_, i) => {
        // Show first, last, current ± 1, and ellipsis
        const show =
          i === 0 ||
          i === totalPages - 1 ||
          Math.abs(i - page) <= 1

        if (!show) {
          // Show single ellipsis between gaps
          if (i === 1 && page > 3) {
            return <span key={i} className="text-gray-400 px-1">…</span>
          }
          if (i === totalPages - 2 && page < totalPages - 4) {
            return <span key={i} className="text-gray-400 px-1">…</span>
          }
          return null
        }

        return (
          <button
            key={i}
            onClick={() => onPageChange(i)}
            className={`px-3 py-1.5 text-sm border rounded-md transition-colors
              ${i === page
                ? 'bg-blue-600 text-white border-blue-600 font-semibold'
                : 'text-gray-600 hover:bg-gray-100 border-gray-300'
              }`}
            aria-label={`Page ${i + 1}`}
            aria-current={i === page ? 'page' : undefined}
          >
            {i + 1}
          </button>
        )
      })}

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages - 1}
        className="px-3 py-1.5 text-sm border rounded-md text-gray-600
          hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed
          transition-colors"
        aria-label="Next page"
      >
        Next →
      </button>
    </nav>
  )
}
