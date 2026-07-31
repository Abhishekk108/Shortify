import { createContext, useCallback, useContext, useReducer } from 'react'

/* ─── Context & reducer ────────────────────────────────────────────────── */

const ToastContext = createContext(null)

let _nextId = 0

function reducer(state, action) {
  switch (action.type) {
    case 'ADD':
      return [...state, action.toast]
    case 'REMOVE':
      return state.filter((t) => t.id !== action.id)
    default:
      return state
  }
}

/* ─── Provider ─────────────────────────────────────────────────────────── */

export function ToastProvider({ children }) {
  const [toasts, dispatch] = useReducer(reducer, [])

  const addToast = useCallback((message, type = 'success', duration = 3000) => {
    const id = ++_nextId
    dispatch({ type: 'ADD', toast: { id, message, type } })
    if (duration > 0) {
      setTimeout(() => dispatch({ type: 'REMOVE', id }), duration)
    }
    return id
  }, [])

  const removeToast = useCallback((id) => {
    dispatch({ type: 'REMOVE', id })
  }, [])

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  )
}

/* ─── Hook ──────────────────────────────────────────────────────────────── */

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>')
  return ctx
}

/* ─── Style map ─────────────────────────────────────────────────────────── */

const STYLES = {
  success: {
    bar: 'bg-green-500',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    ),
    iconBg: 'bg-green-100 text-green-700',
    text: 'text-gray-800',
  },
  error: {
    bar: 'bg-red-500',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
      </svg>
    ),
    iconBg: 'bg-red-100 text-red-700',
    text: 'text-gray-800',
  },
  info: {
    bar: 'bg-blue-500',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    iconBg: 'bg-blue-100 text-blue-700',
    text: 'text-gray-800',
  },
  warning: {
    bar: 'bg-yellow-500',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none"
        viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667
             1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464
             0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    iconBg: 'bg-yellow-100 text-yellow-700',
    text: 'text-gray-800',
  },
}

/* ─── Single toast ──────────────────────────────────────────────────────── */

function Toast({ toast, onRemove }) {
  const s = STYLES[toast.type] ?? STYLES.info
  return (
    <div
      role="alert"
      aria-live="polite"
      className="flex items-start gap-3 w-80 bg-white border border-gray-200
        rounded-xl shadow-lg overflow-hidden animate-slide-in"
    >
      {/* Accent bar */}
      <div className={`w-1 self-stretch shrink-0 ${s.bar}`} aria-hidden="true" />

      {/* Icon */}
      <span className={`mt-3 shrink-0 w-6 h-6 rounded-full flex items-center
        justify-center ${s.iconBg}`}>
        {s.icon}
      </span>

      {/* Message */}
      <p className={`flex-1 py-3 pr-1 text-sm ${s.text}`}>
        {toast.message}
      </p>

      {/* Dismiss */}
      <button
        onClick={() => onRemove(toast.id)}
        className="mt-2.5 mr-2 shrink-0 text-gray-400 hover:text-gray-600
          transition-colors p-1 rounded"
        aria-label="Dismiss notification"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}

/* ─── Container ─────────────────────────────────────────────────────────── */

function ToastContainer({ toasts, onRemove }) {
  if (toasts.length === 0) return null
  return (
    <div
      aria-label="Notifications"
      className="fixed bottom-5 right-5 z-50 flex flex-col gap-3 items-end"
    >
      {toasts.map((t) => (
        <Toast key={t.id} toast={t} onRemove={onRemove} />
      ))}
    </div>
  )
}
