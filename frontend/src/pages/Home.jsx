import ShortenForm from '../components/ShortenForm'

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Hero section */}
      <section className="max-w-2xl mx-auto px-4 pt-16 pb-12 text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-3 tracking-tight">
          Shorten your links
        </h1>
        <p className="text-gray-500 text-base mb-10">
          Paste a long URL below and get a short, shareable link instantly.
          Track clicks in your dashboard.
        </p>

        {/* Form card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 text-left">
          <ShortenForm />
        </div>
      </section>

      {/* Feature callouts */}
      <section className="max-w-2xl mx-auto px-4 pb-16">
        <div className="grid grid-cols-3 gap-4 text-center text-sm text-gray-500">
          <div className="p-4">
            <div className="flex justify-center mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-blue-500" fill="none"
                viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <p className="font-medium text-gray-700">Instant</p>
            <p>Links created in milliseconds</p>
          </div>
          <div className="p-4">
            <div className="flex justify-center mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-blue-500" fill="none"
                viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0
                     0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0
                     0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="font-medium text-gray-700">Analytics</p>
            <p>Track every click</p>
          </div>
          <div className="p-4">
            <div className="flex justify-center mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-blue-500" fill="none"
                viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2
                     2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <p className="font-medium text-gray-700">Custom aliases</p>
            <p>Memorable short codes</p>
          </div>
        </div>
      </section>
    </main>
  )
}
