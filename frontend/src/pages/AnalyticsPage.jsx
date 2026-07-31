import { useParams } from 'react-router-dom'

export default function AnalyticsPage() {
  const { id } = useParams()

  return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">
        Analytics — URL #{id}
      </h1>
      <p className="text-gray-400 text-sm italic">Charts coming in Phase 9</p>
    </main>
  )
}
