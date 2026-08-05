import { useState } from 'react'
import ShortenForm from '../components/ShortenForm'

const faqs = [
  {
    question: 'Are the short URLs permanent?',
    answer:
      'Yes. All short links created with Shortify remain active unless deleted by the owner or disabled by the administrator. There are no click limits.',
  },
  {
    question: 'Can I create links without an account?',
    answer:
      'Yes. Guests can create up to 3 short links per day. Create a free account to get unlimited link creation, analytics, and a personal dashboard.',
  },
  {
    question: 'Why should I use a URL shortener?',
    answer:
      'Short links are cleaner, easier to share, and look more professional. They also save space in messages and social media posts.',
  },
  {
    question: 'Can I track link analytics?',
    answer:
      'Yes. Registered users can view click analytics and manage all their links from the dashboard.',
  },
  {
    question: 'Can I create custom aliases?',
    answer:
      'Yes. You can choose a custom alias (if available) to create memorable and branded short URLs.',
  },
  {
    question: 'Is Shortify secure?',
    answer:
      'Yes. Shortify uses JWT authentication for user accounts and validates URLs before creating short links.',
  },
]

export default function Home() {
  const [openIndex, setOpenIndex] = useState(0)

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
      <section className="max-w-2xl mx-auto px-4 pb-10">
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

      {/* FAQ section */}
      <section className="max-w-3xl mx-auto px-4 pb-16">
        <div className="mb-6 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-blue-600">
            FAQ
          </p>
          <h2 className="mt-2 text-2xl font-bold text-gray-900 sm:text-3xl">
            Frequently asked questions
          </h2>
        </div>

        <div className="space-y-3">
          {faqs.map((item, index) => {
            const isOpen = openIndex === index

            return (
              <div
                key={item.question}
                className={`rounded-2xl border bg-white shadow-sm transition-all duration-300 ${
                  isOpen
                    ? 'border-blue-200 shadow-blue-100/70'
                    : 'border-gray-200 hover:border-blue-200'
                }`}
              >
                <button
                  type="button"
                  onClick={() => setOpenIndex(isOpen ? -1 : index)}
                  className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                  aria-expanded={isOpen}
                  aria-controls={`faq-panel-${index}`}
                >
                  <span className="text-sm font-semibold text-gray-900 sm:text-base">
                    {item.question}
                  </span>
                  <span
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border transition-colors ${
                      isOpen
                        ? 'border-blue-600 bg-blue-600 text-white'
                        : 'border-gray-300 bg-gray-50 text-blue-600'
                    }`}
                    aria-hidden="true"
                  >
                    {isOpen ? '−' : '+'}
                  </span>
                </button>

                <div
                  id={`faq-panel-${index}`}
                  className={`grid transition-all duration-300 ease-out ${
                    isOpen ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'
                  }`}
                >
                  <div className="overflow-hidden">
                    <p className="px-5 pb-5 text-sm leading-6 text-gray-600 sm:text-[15px]">
                      {item.answer}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </section>
    </main>
  )
}
