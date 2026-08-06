import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { isAuthenticated, subscribeToAuthChanges } from '../api/axiosClient'

export default function Footer() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated())

  useEffect(() => {
    const unsubscribe = subscribeToAuthChanges((token) => {
      setAuthenticated(Boolean(token))
    })
    return unsubscribe
  }, [])

  const linkClass =
    'text-blue-200 hover:text-white transition-colors text-sm'

  return (
    <footer className="bg-blue-700 text-white mt-auto">
      <div className="max-w-5xl mx-auto px-4 py-10">

        {/* ── Top row ──────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-8">

          {/* Brand block */}
          <div className="max-w-xs">
            <Link
              to="/"
              className="inline-flex items-center gap-2 text-white font-bold text-lg
                hover:text-blue-100 transition-colors"
              aria-label="Shortify home"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2.5}
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0
                     105.656 5.656l1.102-1.101m-.758-4.899a4 4 0
                     005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                />
              </svg>
              Shortify
            </Link>
            <p className="mt-2 text-blue-200 text-sm leading-relaxed">
              Turn long URLs into clean, shareable short links — and track
              every click with built-in analytics.
            </p>
          </div>

          {/* Quick links */}
          <nav aria-label="Footer navigation">
            <p className="text-xs font-semibold uppercase tracking-widest text-blue-300 mb-3">
              Quick links
            </p>
            <ul className="space-y-2">
              <li>
                <Link to="/" className={linkClass}>
                  Home
                </Link>
              </li>
              {authenticated ? (
                <li>
                  <Link to="/dashboard" className={linkClass}>
                    Dashboard
                  </Link>
                </li>
              ) : (
                <>
                  <li>
                    <Link to="/login" className={linkClass}>
                      Login
                    </Link>
                  </li>
                  <li>
                    <Link to="/register" className={linkClass}>
                      Register
                    </Link>
                  </li>
                </>
              )}
            </ul>
          </nav>
        </div>

        {/* ── Divider ───────────────────────────────────────────────────── */}
        <div className="border-t border-blue-600 mt-8 pt-6 flex flex-col sm:flex-row
          sm:items-center sm:justify-between gap-3 text-blue-300 text-xs">
          <p>© 2026 Shortify. All rights reserved.</p>
          <p className="text-blue-400">
            Built with FastAPI &amp; React
          </p>
        </div>

      </div>
    </footer>
  )
}
