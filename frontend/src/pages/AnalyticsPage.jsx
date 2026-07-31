import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import axiosClient from '../api/axiosClient'
import ClicksChart from '../components/ClicksChart'

/* ─── Helpers ──────────────────────────────────────────────────────────── */

function fmt(dateStr) {
  return new Date(dateStr).toLocaleString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function fmtShort(dateStr) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

/* ─── Skeleton ─────────────────────────────────────────────────────────── */
function Skeleton() {
  return (
    <div className="animate-pulse space-y-6" role="status" aria-label="Loading analytics">
      <div className="h-8 bg-gray-200 rounded w-1/2" />
      <div className="grid grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-24 bg-gray-200 rounded-xl" />
        ))}
      </div>
      <div className="h-56 bg-gray-200 rounded-xl" />
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-10 bg-gray-200 rounded" />
        ))}
      </div>
    </div>
  )
}

/* ─── Stat card ────────────────────────────────────────────────────────── */
function StatCard({ icon, label, value, sub }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl px-5 py-4 shadow-sm">
      <p className="flex items-center gap-1.5 text-xs text-gray-500 font-medium
        uppercase tracking-wide mb-1">
        <span className="text-blue-500">{icon}</span>
        {label}
      </p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  )
}

/* ─── Click table ──────────────────────────────────────────────────────── */
function ClickTable({ clicks }) {
  const [page, setPage] = useState(0)
  const PAGE = 10
  const total = clicks.length
  const totalPages = Math.ceil(total / PAGE)
  const slice = clicks.slice(page * PAGE, page * PAGE + PAGE)

  if (clicks.length === 0) {
    return (
      <div className="text-center py-10 text-gray-400 text-sm">
        No clicks recorded yet.
      </div>
    )
  }

  return (
    <div>
      <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-gray-600">#</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-600">Time</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-600">IP address</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-600">Referrer</th>
              <th className="px-4 py-3 text-left font-semibold text-gray-600">User agent</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {slice.map((click, i) => (
              <tr key={click.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 text-gray-400 tabular-nums">
                  {page * PAGE + i + 1}
                </td>
                <td className="px-4 py-3 text-gray-700 whitespace-nowrap">
                  {fmt(click.clicked_at)}
                </td>
                <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                  {click.ip_address ?? '—'}
                </td>
                <td className="px-4 py-3 text-gray-500 max-w-[160px]">
                  {click.referrer ? (
                    <span className="truncate block" title={click.referrer}>
                      {click.referrer}
                    </span>
                  ) : (
                    <span className="text-gray-300">direct</span>
                  )}
                </td>
                <td className="px-4 py-3 text-gray-400 max-w-[200px]">
                  <span className="truncate block text-xs" title={click.user_agent ?? ''}>
                    {click.user_agent ?? '—'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex justify-center gap-2">
          <button
            onClick={() => setPage((p) => p - 1)}
            disabled={page === 0}
            className="px-3 py-1.5 text-sm border rounded-md text-gray-600
              hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed
              transition-colors"
          >
            ← Prev
          </button>
          <span className="px-3 py-1.5 text-sm text-gray-500">
            {page + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= totalPages - 1}
            className="px-3 py-1.5 text-sm border rounded-md text-gray-600
              hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed
              transition-colors"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}

/* ─── Main page ────────────────────────────────────────────────────────── */
export default function AnalyticsPage() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    axiosClient
      .get(`/api/urls/${id}/analytics`)
      .then(({ data }) => setData(data))
      .catch((err) =>
        setError(err?.response?.data?.detail ?? 'Failed to load analytics.')
      )
      .finally(() => setLoading(false))
  }, [id])

  /* ── loading ── */
  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-10">
          <Skeleton />
        </div>
      </main>
    )
  }

  /* ── error ── */
  if (error) {
    return (
      <main className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-10">
          <div role="alert"
            className="px-4 py-3 bg-red-50 border border-red-200 rounded-lg
              text-sm text-red-700 mb-4">
            {error}
          </div>
          <Link to="/dashboard"
            className="text-sm text-blue-600 hover:underline">
            ← Back to Dashboard
          </Link>
        </div>
      </main>
    )
  }

  /* ── first + last click dates ── */
  const clicks = data.clicks ?? []
  const sorted = [...clicks].sort(
    (a, b) => new Date(a.clicked_at) - new Date(b.clicked_at)
  )
  const firstClick = sorted[0]?.clicked_at
  const lastClick = sorted[sorted.length - 1]?.clicked_at

  /* ── unique IPs ── */
  const uniqueIps = new Set(clicks.map((c) => c.ip_address).filter(Boolean)).size

  /* ── top referrers ── */
  const referrerCounts = clicks.reduce((acc, c) => {
    const r = c.referrer ?? 'Direct'
    acc[r] = (acc[r] ?? 0) + 1
    return acc
  }, {})
  const topReferrers = Object.entries(referrerCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5)

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">

        {/* ── Breadcrumb ──────────────────────────────────────────────── */}
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Link to="/dashboard" className="hover:text-blue-600 transition-colors">
            Dashboard
          </Link>
          <span>/</span>
          <span className="text-gray-800 font-medium">Analytics</span>
        </div>

        {/* ── Page title ──────────────────────────────────────────────── */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Analytics — <span className="text-blue-600">/{data.short_code}</span>
          </h1>
          <p className="text-sm text-gray-500 mt-1 truncate">
            {data.original_url}
          </p>
        </div>

        {/* ── Stat cards ──────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
                viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5" />
              </svg>
            }
            label="Total clicks"
            value={data.total_clicks}
          />
          <StatCard
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
                viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945
                     M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104
                     0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064
                     M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            label="Unique IPs"
            value={uniqueIps}
          />
          <StatCard
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
                viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0
                     00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            }
            label="First click"
            value={firstClick ? fmtShort(firstClick) : '—'}
          />
          <StatCard
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
                viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            label="Last click"
            value={lastClick ? fmtShort(lastClick) : '—'}
          />
        </div>

        {/* ── Clicks per day chart ─────────────────────────────────────── */}
        <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
          <h2 className="text-base font-semibold text-gray-700 mb-4">
            Clicks per day
          </h2>
          <ClicksChart clicks={clicks} />
        </section>

        {/* ── Top referrers ───────────────────────────────────────────── */}
        {topReferrers.length > 0 && (
          <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
            <h2 className="text-base font-semibold text-gray-700 mb-4">
              Top referrers
            </h2>
            <ul className="space-y-2">
              {topReferrers.map(([referrer, count]) => {
                const pct = Math.round((count / clicks.length) * 100)
                return (
                  <li key={referrer} className="flex items-center gap-3">
                    <span
                      className="text-sm text-gray-600 truncate flex-1"
                      title={referrer}
                    >
                      {referrer}
                    </span>
                    <div className="flex items-center gap-2 shrink-0">
                      <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-8 text-right">
                        {count}
                      </span>
                    </div>
                  </li>
                )
              })}
            </ul>
          </section>
        )}

        {/* ── Recent clicks timeline ───────────────────────────────────── */}
        <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
          <h2 className="text-base font-semibold text-gray-700 mb-4">
            Click history
            <span className="ml-2 text-xs font-normal text-gray-400">
              ({clicks.length} total)
            </span>
          </h2>
          <ClickTable clicks={clicks} />
        </section>

      </div>
    </main>
  )
}
