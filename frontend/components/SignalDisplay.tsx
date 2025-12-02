'use client'

interface SignalDisplayProps {
  signal: string
  score: number
  confidence: string
  ticker: string
}

export default function SignalDisplay({ signal, score, confidence, ticker }: SignalDisplayProps) {
  // Determine colors based on signal
  const getSignalColor = () => {
    if (signal.includes('BUY') || signal.includes('OPPORTUNITY')) {
      return {
        bg: 'from-green-600 to-green-700',
        border: 'border-green-400',
        glow: 'shadow-green-500/25'
      }
    }
    if (signal.includes('SELL')) {
      return {
        bg: 'from-red-600 to-red-700',
        border: 'border-red-400',
        glow: 'shadow-red-500/25'
      }
    }
    return {
      bg: 'from-yellow-600 to-yellow-700',
      border: 'border-yellow-400',
      glow: 'shadow-yellow-500/25'
    }
  }

  const colors = getSignalColor()
  
  // Clean up signal text for display
  const cleanSignal = signal.replace(/^[🚀🔻📈📉⏸️⚠️🚨]+\s*/, '').replace(/\s*-.*/, '')
  const signalType = signal.split(' - ')[1] || ''

  return (
    <div className={`relative bg-gradient-to-br ${colors.bg} ${colors.border} border-2 rounded-2xl p-8 ${colors.glow} shadow-2xl overflow-hidden`}>
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent"></div>
      
      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-4xl font-bold text-white mb-2">{ticker}</h2>
            <div className="text-white/80 text-sm font-medium">
              Live Analysis • Hedge Fund Grade
            </div>
          </div>
          <div className="text-right">
            <div className="text-white/60 text-xs uppercase tracking-wider mb-1">
              Confidence
            </div>
            <div className="text-white text-lg font-semibold">
              {confidence.replace('(STANDARD)', '').replace('(REGIME-BOOSTED)', '⚡')}
            </div>
          </div>
        </div>

        {/* Main Signal */}
        <div className="mb-4">
          <div className="text-white text-5xl font-black mb-2">
            {cleanSignal}
          </div>
          {signalType && (
            <div className="text-white/80 text-xl font-medium">
              {signalType}
            </div>
          )}
        </div>

        {/* Score Display */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-white/60 text-sm uppercase tracking-wider">
              Algorithm Score
            </div>
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
              <span className="text-white text-2xl font-bold">
                {score.toFixed(1)}
              </span>
              <span className="text-white/80 text-lg">/100</span>
            </div>
          </div>
          
          {/* Pulse Animation for Strong Signals */}
          {(signal.includes('STRONG') || signal.includes('CRISIS')) && (
            <div className="animate-pulse">
              <div className="w-4 h-4 bg-white rounded-full"></div>
            </div>
          )}
        </div>
      </div>

      {/* Animated Background Elements */}
      <div className="absolute top-4 right-4 w-32 h-32 bg-white/5 rounded-full blur-xl"></div>
      <div className="absolute bottom-4 left-4 w-24 h-24 bg-white/5 rounded-full blur-lg"></div>
    </div>
  )
}
