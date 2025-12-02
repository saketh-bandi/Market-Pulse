'use client'

interface RegimeIndicatorProps {
  regime: string
  vix: number
  weights: {
    sentiment: number
    gamma: number
    volume: number
    valuation: number
  }
}

export default function RegimeIndicator({ regime, vix, weights }: RegimeIndicatorProps) {
  const getRegimeConfig = (regimeType: string) => {
    switch (regimeType) {
      case 'FEAR':
        return {
          color: 'from-red-500 to-red-600',
          icon: '🔥',
          description: 'High Volatility - Math Over Hype',
          borderColor: 'border-red-400'
        }
      case 'COMPLACENCY':
        return {
          color: 'from-green-500 to-green-600',
          icon: '😴',
          description: 'Low Volatility - Sentiment Driven',
          borderColor: 'border-green-400'
        }
      default:
        return {
          color: 'from-blue-500 to-blue-600',
          icon: '📊',
          description: 'Normal Market - Balanced Approach',
          borderColor: 'border-blue-400'
        }
    }
  }

  const config = getRegimeConfig(regime)

  return (
    <div className={`bg-gradient-to-r ${config.color} ${config.borderColor} border rounded-xl p-4`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{config.icon}</span>
          <div>
            <h3 className="text-white font-bold text-lg">{regime} REGIME</h3>
            <p className="text-white/80 text-sm">{config.description}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-white/60 text-xs uppercase">VIX</div>
          <div className="text-white text-xl font-bold">{vix.toFixed(1)}</div>
        </div>
      </div>

      {/* Weight Distribution */}
      <div className="bg-black/20 rounded-lg p-3">
        <div className="text-white/80 text-xs uppercase tracking-wider mb-2">
          Dynamic Algorithm Weights
        </div>
        <div className="grid grid-cols-4 gap-2 text-xs">
          <div className="text-center">
            <div className="text-white/60">Sentiment</div>
            <div className="text-white font-bold">{(weights.sentiment * 100).toFixed(0)}%</div>
            <div className="bg-white/20 rounded-full h-1 mt-1">
              <div 
                className="bg-white rounded-full h-1 transition-all duration-500"
                style={{ width: `${weights.sentiment * 100}%` }}
              />
            </div>
          </div>
          <div className="text-center">
            <div className="text-white/60">Gamma</div>
            <div className="text-white font-bold">{(weights.gamma * 100).toFixed(0)}%</div>
            <div className="bg-white/20 rounded-full h-1 mt-1">
              <div 
                className="bg-white rounded-full h-1 transition-all duration-500"
                style={{ width: `${weights.gamma * 100}%` }}
              />
            </div>
          </div>
          <div className="text-center">
            <div className="text-white/60">Volume</div>
            <div className="text-white font-bold">{(weights.volume * 100).toFixed(0)}%</div>
            <div className="bg-white/20 rounded-full h-1 mt-1">
              <div 
                className="bg-white rounded-full h-1 transition-all duration-500"
                style={{ width: `${weights.volume * 100}%` }}
              />
            </div>
          </div>
          <div className="text-center">
            <div className="text-white/60">Valuation</div>
            <div className="text-white font-bold">{(weights.valuation * 100).toFixed(0)}%</div>
            <div className="bg-white/20 rounded-full h-1 mt-1">
              <div 
                className="bg-white rounded-full h-1 transition-all duration-500"
                style={{ width: `${weights.valuation * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
