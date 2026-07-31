import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

/**
 * ClicksChart — bar chart showing clicks per day.
 *
 * Props:
 *   clicks: array of click objects { clicked_at, ... }
 */
export default function ClicksChart({ clicks = [] }) {
  // Aggregate clicks by calendar day (YYYY-MM-DD)
  const countsByDay = clicks.reduce((acc, click) => {
    const day = click.clicked_at.slice(0, 10) // "2026-07-28"
    acc[day] = (acc[day] ?? 0) + 1
    return acc
  }, {})

  // Sort chronologically and format label to "Jul 28"
  const data = Object.entries(countsByDay)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, count]) => ({
      date,
      label: new Date(date + 'T00:00:00').toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      }),
      clicks: count,
    }))

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
        No click data to chart yet.
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart
        data={data}
        margin={{ top: 8, right: 16, left: -8, bottom: 0 }}
        aria-label="Clicks per day bar chart"
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 12, fill: '#6b7280' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          allowDecimals={false}
          tick={{ fontSize: 12, fill: '#6b7280' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          cursor={{ fill: '#eff6ff' }}
          contentStyle={{
            borderRadius: '8px',
            border: '1px solid #e5e7eb',
            fontSize: '13px',
          }}
          formatter={(value) => [value, 'Clicks']}
        />
        <Bar dataKey="clicks" fill="#3b82f6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
