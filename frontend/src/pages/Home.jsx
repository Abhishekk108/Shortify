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
            <p className="text-2xl mb-1">⚡</p>
            <p className="font-medium text-gray-700">Instant</p>
            <p>Links created in milliseconds</p>
          </div>
          <div className="p-4">
            <p className="text-2xl mb-1">📊</p>
            <p className="font-medium text-gray-700">Analytics</p>
            <p>Track every click</p>
          </div>
          <div className="p-4">
            <p className="text-2xl mb-1">✏️</p>
            <p className="font-medium text-gray-700">Custom aliases</p>
            <p>Memorable short codes</p>
          </div>
        </div>
      </section>
    </main>
  )
}
