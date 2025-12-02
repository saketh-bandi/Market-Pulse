'use client'

import { useState } from 'react'
import { Search, Activity, Database, Wifi } from 'lucide-react'

interface AnalysisResult {
  ticker: string
  source: string
  data: {
    '🎯 TICKER': string
    '📊 FINAL SCORE': string
    '🎪 TRADING SIGNAL': string
    '🎯 CONFIDENCE': string
    '📋 COMPONENT SCORES': {
      '💭 Sentiment': string
      '🚀 Gamma': string
      '⚖️ Volume Bias': string
      '💰 Valuation': string
    }
    '🔬 ADVANCED METRICS'?: {
      'Market Regime': string
      'Linear Score': string
      'Non-Linear Score': string
      'Z-Scores': string
    }
    '⚖️ DYNAMIC WEIGHTS'?: {
      sentiment: number
      gamma: number
      volume: number
      valuation: number
    }
  }
}

export default function MarketPulseTerminal() {
  const [ticker, setTicker] = useState('NVDA')
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyzeStock = async () => {
    if (!ticker.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analyze/${ticker.toUpperCase()}`)
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`)
      }
      
      const data = await response.json()
      setAnalysis(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-lg border-b border-green-400/20 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Activity size={32} className="text-green-400" />
            <div>
              <h1 className="text-2xl font-bold text-white">MarketPulse Terminal</h1>
              <p className="text-gray-400 text-sm">Professional Financial Intelligence Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2 text-green-400">
              <Wifi size={16} />
              <span>API Connected</span>
            </div>
            <div className="flex items-center gap-2 text-blue-400">
              <Database size={16} />
              <span>Cache Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6 space-y-8">
        
        {/* Search Section */}
        <div className="text-center space-y-6">
          <h2 className="text-3xl font-bold text-white">Stock Analysis</h2>
          <div className="max-w-md mx-auto flex gap-4">
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="Enter ticker (NVDA, TSLA, AAPL)"
              className="flex-1 bg-gray-800/50 border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-400"
              onKeyPress={(e) => e.key === 'Enter' && analyzeStock()}
            />
            <button
              onClick={analyzeStock}
              disabled={loading || !ticker.trim()}
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-600 disabled:to-gray-700 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-200 flex items-center gap-2"
            >
              <Search className="h-5 w-5" />
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/50 border border-red-500/30 rounded-xl p-4 text-center">
            <p className="text-red-300">Error: {error}</p>
          </div>
        )}

        {/* Results */}
        {analysis && (
          <div className="space-y-6">
            
            {/* 🚀 BIG VERDICT CARD - Pro Style */}
            <div className={`relative overflow-hidden rounded-2xl p-8 text-center shadow-2xl ${
              analysis.data['🎪 TRADING SIGNAL']?.includes('BUY') 
                ? 'bg-gradient-to-br from-green-600/80 to-green-700/80 border-2 border-green-400' 
                : analysis.data['🎪 TRADING SIGNAL']?.includes('SELL')
                ? 'bg-gradient-to-br from-red-600/80 to-red-700/80 border-2 border-red-400'
                : 'bg-gradient-to-br from-yellow-600/80 to-yellow-700/80 border-2 border-yellow-400'
            }`}>
              <div className="relative z-10">
                <h3 className="text-4xl font-bold text-white mb-2">
                  {analysis.data['🎯 TICKER']?.replace('🎯 ', '') || analysis.ticker}
                </h3>
                
                <div className="text-6xl font-black mb-6 text-white">
                  {analysis.data['🎪 TRADING SIGNAL']?.replace(/^[🚀🔻📈📉⏸️⚠️🚨]+\s*/, '').split(' - ')[0] || 'HOLD'}
                </div>
                
                <div className="grid grid-cols-2 gap-6 max-w-md mx-auto">
                  <div className="bg-black/20 rounded-xl p-4 backdrop-blur-sm">
                    <div className="text-white/70 text-sm mb-1">Algorithm Score</div>
                    <div className="text-3xl font-bold text-white">
                      {analysis.data['📊 FINAL SCORE'] || 'N/A'}
                    </div>
                  </div>
                  <div className="bg-black/20 rounded-xl p-4 backdrop-blur-sm">
                    <div className="text-white/70 text-sm mb-1">Confidence</div>
                    <div className="text-3xl font-bold text-white">
                      {analysis.data['🎯 CONFIDENCE']?.replace('🎯 ', '').split(' ')[0] || 'N/A'}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Background Effects */}
              <div className="absolute top-4 right-4 w-32 h-32 bg-white/10 rounded-full blur-xl"></div>
              <div className="absolute bottom-4 left-4 w-24 h-24 bg-white/10 rounded-full blur-lg"></div>
            </div>

            {/* 📊 Component Scores - Professional Grid */}
            <div className="bg-gray-900/80 backdrop-blur-sm border border-gray-600/30 rounded-2xl p-8">
              <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                📊 Component Analysis Dashboard
              </h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {analysis.data['📋 COMPONENT SCORES'] && Object.entries(analysis.data['📋 COMPONENT SCORES']).map(([component, score]) => {
                  const cleanComponent = component.replace(/^[💭🚀⚖️💰]\s*/, '')
                  const numericScore = score && typeof score === 'string' ? parseFloat(score.split('/')[0]) : 0
                  
                  // Component-specific colors
                  const componentColors = {
                    'Sentiment': { bg: 'from-amber-500/20 to-orange-500/20', border: 'border-amber-400/30', text: 'text-amber-300' },
                    'Gamma': { bg: 'from-red-500/20 to-pink-500/20', border: 'border-red-400/30', text: 'text-red-300' },
                    'Volume Bias': { bg: 'from-blue-500/20 to-cyan-500/20', border: 'border-blue-400/30', text: 'text-blue-300' },
                    'Valuation': { bg: 'from-green-500/20 to-emerald-500/20', border: 'border-green-400/30', text: 'text-green-300' }
                  }
                  
                  const colorConfig = componentColors[cleanComponent as keyof typeof componentColors] || 
                    { bg: 'from-gray-500/20 to-gray-600/20', border: 'border-gray-400/30', text: 'text-gray-300' }
                  
                  return (
                    <div key={component} className={`bg-gradient-to-br ${colorConfig.bg} ${colorConfig.border} border rounded-xl p-6 text-center hover:scale-105 transition-all duration-300`}>
                      <h4 className={`${colorConfig.text} text-xs font-medium mb-3 uppercase tracking-wider`}>
                        {cleanComponent}
                      </h4>
                      <div className="text-3xl font-bold text-white mb-4">
                        {numericScore.toFixed(1)}
                      </div>
                      <div className="text-sm text-gray-400 mb-3">
                        {score || 'N/A'}
                      </div>
                      <div className="bg-gray-700/50 rounded-full h-3 overflow-hidden">
                        <div 
                          className={`h-3 rounded-full transition-all duration-1000 ${
                            numericScore >= 75 ? 'bg-gradient-to-r from-green-400 to-green-500' : 
                            numericScore <= 25 ? 'bg-gradient-to-r from-red-400 to-red-500' : 'bg-gradient-to-r from-yellow-400 to-yellow-500'
                          }`}
                          style={{ width: `${Math.max(0, Math.min(100, numericScore))}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* 🚀 Advanced Metrics */}
            {analysis.data['🔬 ADVANCED METRICS'] && (
              <div className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 backdrop-blur-sm border border-blue-500/30 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-blue-300 mb-6 flex items-center gap-2">
                  🚀 Hedge Fund Grade Metrics
                  <span className="text-xs bg-blue-500/20 px-3 py-1 rounded-full">v2.0</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-800/40 rounded-xl p-4 text-center">
                    <div className="text-blue-300 text-xs mb-2 uppercase tracking-wider">Market Regime</div>
                    <div className="text-white font-bold text-lg">
                      {analysis.data['🔬 ADVANCED METRICS']['Market Regime']?.split(' ')[0] || 'Normal'}
                    </div>
                  </div>
                  <div className="bg-gray-800/40 rounded-xl p-4 text-center">
                    <div className="text-green-300 text-xs mb-2 uppercase tracking-wider">Linear Score</div>
                    <div className="text-white font-bold text-lg">
                      {analysis.data['🔬 ADVANCED METRICS']['Linear Score'] || 'N/A'}
                    </div>
                  </div>
                  <div className="bg-gray-800/40 rounded-xl p-4 text-center">
                    <div className="text-purple-300 text-xs mb-2 uppercase tracking-wider">Non-Linear Score</div>
                    <div className="text-white font-bold text-lg">
                      {analysis.data['🔬 ADVANCED METRICS']['Non-Linear Score'] || 'N/A'}
                    </div>
                  </div>
                </div>

                {/* Dynamic Weights Display */}
                {analysis.data['⚖️ DYNAMIC WEIGHTS'] && (
                  <div className="mt-6 bg-gray-800/40 rounded-xl p-4">
                    <div className="text-cyan-300 text-sm font-medium mb-3">Dynamic Algorithm Weights</div>
                    <div className="grid grid-cols-4 gap-2 text-xs">
                      <div className="text-center">
                        <div className="text-gray-400">Sentiment</div>
                        <div className="text-white font-bold">
                          {(analysis.data['⚖️ DYNAMIC WEIGHTS'].sentiment * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-gray-400">Gamma</div>
                        <div className="text-white font-bold">
                          {(analysis.data['⚖️ DYNAMIC WEIGHTS'].gamma * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-gray-400">Volume</div>
                        <div className="text-white font-bold">
                          {(analysis.data['⚖️ DYNAMIC WEIGHTS'].volume * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-gray-400">Valuation</div>
                        <div className="text-white font-bold">
                          {(analysis.data['⚖️ DYNAMIC WEIGHTS'].valuation * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="mt-12 pt-8 border-t border-gray-700/30 text-center text-sm text-gray-400">
        <p>MarketPulse Terminal v2.0 - Hedge Fund Grade Algorithm</p>
        <p className="mt-1">Not financial advice. For informational purposes only.</p>
      </footer>
    </div>
  )
}
