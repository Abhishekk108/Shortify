/**
 * SearchBar — controlled search input.
 * Props:
 *   value: string
 *   onChange: (value: string) => void
 *   placeholder: string (optional)
 */
export default function SearchBar({ value, onChange, placeholder = 'Search links…' }) {
  return (
    <div className="relative w-full max-w-sm">
      {/* Search icon */}
      <span className="absolute inset-y-0 left-3 flex items-center text-gray-400 pointer-events-none">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>
      </span>

      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg
                   bg-white focus:outline-none focus:ring-2 focus:ring-blue-500
                   focus:border-transparent placeholder-gray-400"
        aria-label="Search links"
      />
    </div>
  )
}
