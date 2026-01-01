import { BarChart, Bar, XAxis, YAxis, Cell, ResponsiveContainer, Tooltip } from 'recharts'

function ShapChart({ factors }) {
  if (!factors || factors.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No SHAP data available
      </div>
    )
  }

  // Transform data for chart
  const chartData = factors.map(factor => ({
    name: factor.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value: factor.direction === 'negative' ? -factor.impact * 100 : factor.impact * 100,
    direction: factor.direction
  })).sort((a, b) => Math.abs(b.value) - Math.abs(a.value))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border">
          <p className="font-semibold">{data.name}</p>
          <p className={data.value >= 0 ? 'text-green-600' : 'text-red-600'}>
            Impact: {data.value >= 0 ? '+' : ''}{data.value.toFixed(1)}%
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 10, right: 30, left: 100, bottom: 10 }}
        >
          <XAxis 
            type="number" 
            domain={[-100, 100]}
            tickFormatter={(value) => `${value}%`}
          />
          <YAxis 
            type="category" 
            dataKey="name"
            tick={{ fontSize: 12 }}
            width={90}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`}
                fill={entry.value >= 0 ? '#22c55e' : '#ef4444'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default ShapChart