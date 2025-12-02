'use client'

import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface GaugeChartProps {
  value: number
  title: string
  color?: string
}

export default function GaugeChart({ value, title, color = '#22c55e' }: GaugeChartProps) {
  // Create gauge data - semicircle gauge
  const gaugeData = [
    { name: 'filled', value: value },
    { name: 'empty', value: 100 - value }
  ]

  // Color based on value
  const getGaugeColor = (val: number) => {
    if (val >= 75) return '#22c55e' // Green
    if (val >= 50) return '#eab308' // Yellow
    if (val >= 25) return '#f97316' // Orange
    return '#ef4444' // Red
  }

  const gaugeColor = color || getGaugeColor(value)

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <div className="relative w-full h-32">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={gaugeData}
              cx="50%"
              cy="90%"
              startAngle={180}
              endAngle={0}
              innerRadius={40}
              outerRadius={60}
              dataKey="value"
              stroke="none"
            >
              <Cell fill={gaugeColor} />
              <Cell fill="rgba(75, 85, 99, 0.3)" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        
        {/* Gauge needle indicator */}
        <div 
          className="absolute bottom-0 left-1/2 w-0.5 h-12 bg-white origin-bottom transform -translate-x-1/2 transition-transform duration-700"
          style={{ 
            transform: `translateX(-50%) rotate(${(value / 100) * 180 - 90}deg)`,
            transformOrigin: 'bottom center'
          }}
        />
        
        {/* Center value display */}
        <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-center">
          <div className="text-2xl font-bold text-white">
            {value.toFixed(1)}
          </div>
        </div>
      </div>
      
      <div className="mt-2 text-center">
        <h4 className="text-sm font-medium text-gray-300 uppercase tracking-wide">
          {title}
        </h4>
      </div>
    </div>
  )
}
