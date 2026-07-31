import { Link, NavLink } from 'react-router-dom'

export default function Navbar() {
  const linkClass = ({ isActive }) =>
    isActive
      ? 'text-white font-semibold border-b-2 border-white pb-0.5'
      : 'text-blue-100 hover:text-white transition-colors'

  return (
    <nav className="bg-blue-600 shadow-md">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="text-white text-xl font-bold tracking-tight">
          ✂️ Shortify
        </Link>

        {/* Nav links */}
        <div className="flex gap-6 text-sm">
          <NavLink to="/" end className={linkClass}>
            Home
          </NavLink>
          <NavLink to="/dashboard" className={linkClass}>
            Dashboard
          </NavLink>
        </div>
      </div>
    </nav>
  )
}
