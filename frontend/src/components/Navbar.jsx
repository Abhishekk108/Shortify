import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { clearAuthToken } from '../api/axiosClient'

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const navigate = useNavigate()
  const token = localStorage.getItem('shortify_access_token')

  const linkClass = ({ isActive }) =>
    isActive
      ? 'text-white font-semibold border-b-2 border-white pb-0.5'
      : 'text-blue-100 hover:text-white transition-colors'

  const mobileLinkClass = ({ isActive }) =>
    `block px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
      isActive
        ? 'bg-blue-700 text-white'
        : 'text-blue-100 hover:bg-blue-700 hover:text-white'
    }`

  function handleLogout() {
    clearAuthToken()
    setMenuOpen(false)
    navigate('/login')
  }

  return (
    <nav className="bg-blue-600 shadow-md">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="text-white text-xl font-bold tracking-tight flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none"
            viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101
                 m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          Shortify
        </Link>

        {/* Desktop nav links */}
        <div className="hidden sm:flex gap-6 text-sm items-center">
          <NavLink to="/" end className={linkClass}>
            Home
          </NavLink>
          {token ? (
            <>
              <NavLink to="/dashboard" className={linkClass}>
                Dashboard
              </NavLink>
              <button
                onClick={handleLogout}
                className="text-blue-100 hover:text-white transition-colors"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={linkClass}>
                Login
              </NavLink>
              <NavLink to="/register" className={linkClass}>
                Register
              </NavLink>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="sm:hidden text-white p-1.5 rounded-md hover:bg-blue-700
            transition-colors"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none"
            viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d={menuOpen
                ? 'M6 18L18 6M6 6l12 12'
                : 'M4 6h16M4 12h16M4 18h16'} />
          </svg>
        </button>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div
          id="mobile-menu"
          className="sm:hidden px-3 pb-3 space-y-1 bg-blue-600 border-t border-blue-500"
        >
          <NavLink
            to="/"
            end
            className={mobileLinkClass}
            onClick={() => setMenuOpen(false)}
          >
            Home
          </NavLink>
          {token ? (
            <>
              <NavLink
                to="/dashboard"
                className={mobileLinkClass}
                onClick={() => setMenuOpen(false)}
              >
                Dashboard
              </NavLink>
              <button
                onClick={handleLogout}
                className="block w-full text-left px-4 py-3 text-sm font-medium rounded-lg text-blue-100 hover:bg-blue-700 hover:text-white"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className={mobileLinkClass}
                onClick={() => setMenuOpen(false)}
              >
                Login
              </NavLink>
              <NavLink
                to="/register"
                className={mobileLinkClass}
                onClick={() => setMenuOpen(false)}
              >
                Register
              </NavLink>
            </>
          )}
        </div>
      )}
    </nav>
  )
}
