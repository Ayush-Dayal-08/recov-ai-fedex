import { useState, useEffect } from 'react'
import ShapChart from './ShapChart'

function AccountDetail({ accountId, onBack }) {
  const [account, setAccount] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchAccount = async () => {
      try {
        setLoading(true)
        const response = await fetch(`http://localhost:8000/account/${accountId}`)
        
        if (!response.ok) {
          throw new Error(`Failed to fetch account: ${response.statusText}`)
        }
        
        const data = await response.json()
        console.log('Account data:', data)
        setAccount(data)
      } catch (err) {
        console.error('Fetch error:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    if (accountId) {
      fetchAccount()
    }
  }, [accountId])

  // Loading State
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-fedex-purple border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing account with AI...</p>
        </div>
      </div>
    )
  }

  // Error State
  if (error) {
    return (
      <div className="max-w-xl mx-auto">
        <button onClick={onBack} className="mb-4 text-fedex-purple hover:text-fedex-orange">
          ← Back to List
        </button>
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <p className="text-red-600 text-lg">❌ {error}</p>
          <p className="text-sm text-gray-500 mt-2">Make sure you've uploaded a CSV first.</p>
        </div>
      </div>
    )
  }

  // Data extraction
  const probability = account?.recovery_probability || 0
  const percentScore = Math.round(probability * 100)
  const riskLevel = account?.risk_level || 'Unknown'
  const expectedDays = account?.expected_days || 'N/A'
  const companyName = account?.company_name || 'Unknown Company'
  const topFactors = account?.top_factors || []
  const dca = account?.recommended_dca || {}

  // Color functions
  const getProgressColor = () => {
    if (percentScore >= 70) return 'from-green-400 to-green-600'
    if (percentScore >= 50) return 'from-yellow-400 to-yellow-600'
    return 'from-red-400 to-red-600'
  }

  const getRiskBadgeColor = () => {
    if (riskLevel === 'Low') return 'bg-green-100 text-green-800 border-green-300'
    if (riskLevel === 'Medium') return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    return 'bg-red-100 text-red-800 border-red-300'
  }

  const formatCurrency = (amount) => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  return (
    <div className="animate-fadeIn">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="mb-6 flex items-center text-fedex-purple hover:text-fedex-orange transition-colors font-medium group"
      >
        <span className="mr-2 group-hover:-translate-x-1 transition-transform">←</span>
        Back to Account List
      </button>

      {/* Company Header Card */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border-l-4 border-fedex-purple">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              🏢 {companyName}
            </h1>
            <p className="text-gray-500 font-mono">Account ID: {accountId}</p>
          </div>
          <div className="mt-4 md:mt-0">
            <span className={`px-4 py-2 rounded-full text-sm font-bold border ${getRiskBadgeColor()}`}>
              {riskLevel} Risk
            </span>
          </div>
        </div>
        
        {/* Quick Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t">
          <div className="text-center p-3 bg-gray-50 rounded-xl">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Amount Owed</p>
            <p className="text-2xl font-bold text-gray-800">{formatCurrency(account?.amount)}</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-xl">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Days Overdue</p>
            <p className="text-2xl font-bold text-gray-800">{account?.days_overdue || 'N/A'}</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-xl">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Expected Recovery</p>
            <p className="text-2xl font-bold text-gray-800">{expectedDays} days</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-xl">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Velocity Score</p>
            <p className="text-2xl font-bold text-gray-800">{account?.recovery_velocity_score || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* 🤖 AI Intelligence Panel - HERO SECTION */}
        <div className="bg-gradient-to-br from-fedex-purple via-purple-700 to-purple-900 rounded-2xl shadow-2xl p-8 text-white relative overflow-hidden">
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"></div>
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2"></div>
          
          <h2 className="text-xl font-bold mb-8 flex items-center relative z-10">
            <span className="text-3xl mr-3">🤖</span>
            AI Recovery Intelligence
          </h2>
          
          {/* Large Probability Display */}
          <div className="text-center mb-8 relative z-10">
            <p className="text-sm uppercase tracking-widest text-purple-200 mb-3">Recovery Probability</p>
            <p className="text-8xl font-black tracking-tight">
              {percentScore}<span className="text-5xl">%</span>
            </p>
          </div>
          
          {/* Animated Progress Bar */}
          <div className="mb-8 relative z-10">
            <div className="w-full bg-purple-900/50 rounded-full h-5 overflow-hidden backdrop-blur">
              <div
                className={`h-5 rounded-full bg-gradient-to-r ${getProgressColor()} transition-all duration-1000 ease-out shadow-lg`}
                style={{ width: `${percentScore}%` }}
              ></div>
            </div>
          </div>
          
          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 relative z-10">
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center border border-white/20">
              <p className="text-xs uppercase tracking-wide text-purple-200 mb-1">Confidence</p>
              <p className="text-2xl font-bold">High</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4 text-center border border-white/20">
              <p className="text-xs uppercase tracking-wide text-purple-200 mb-1">Est. Days</p>
              <p className="text-2xl font-bold">{expectedDays}</p>
            </div>
          </div>
        </div>

        {/* 📊 Key Factors Panel */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="text-2xl mr-3">📊</span>
            Key Factors (SHAP Analysis)
          </h2>
          
          <div className="space-y-3">
            {topFactors.length > 0 ? (
              topFactors.map((factor, index) => {
                const isPositive = factor.direction === 'positive'
                const isNegative = factor.direction === 'negative'
                const impactValue = (factor.impact * 100).toFixed(0)
                
                return (
                  <div 
                    key={index}
                    className={`p-4 rounded-xl border-2 transition-all hover:scale-[1.02] ${
                      isPositive 
                        ? 'bg-green-50 border-green-200 hover:shadow-green-100' 
                        : isNegative 
                          ? 'bg-red-50 border-red-200 hover:shadow-red-100'
                          : 'bg-gray-50 border-gray-200'
                    } hover:shadow-lg`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <span className="text-2xl mr-3">
                          {isPositive ? '✅' : isNegative ? '⚠️' : '➖'}
                        </span>
                        <div>
                          <p className="font-semibold text-gray-800 capitalize">
                            {factor.feature.replace(/_/g, ' ')}
                          </p>
                          <p className={`text-sm font-medium ${
                            isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-500'
                          }`}>
                            {isPositive ? '+' : isNegative ? '-' : ''}{impactValue}% impact
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })
            ) : (
              <p className="text-gray-500 text-center py-8">No factor data available</p>
            )}
          </div>
        </div>

        {/* 🏆 DCA Recommendation */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="text-2xl mr-3">🏆</span>
            Recommended Collection Agency
          </h2>
          
          <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 rounded-xl p-6 border-2 border-blue-200">
            <div className="flex items-start">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-2xl w-14 h-14 flex items-center justify-center text-2xl font-bold mr-4 flex-shrink-0 shadow-lg">
                {dca.name ? dca.name.charAt(0) : '?'}
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800">
                  {dca.name || 'No recommendation'}
                </h3>
                <p className="text-blue-600 font-semibold mt-1">
                  🎯 {dca.specialization || 'General collections'}
                </p>
                <p className="text-gray-600 mt-3 leading-relaxed">
                  💡 {dca.reasoning || 'Based on account analysis'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 📋 Strategy Section */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="text-2xl mr-3">📋</span>
            Recovery Strategy
          </h2>
          
          <div className="space-y-3">
            <div className="flex items-start p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200 hover:shadow-md transition-shadow">
              <span className="text-2xl mr-4">1️⃣</span>
              <div>
                <p className="font-bold text-gray-800">Initial Contact</p>
                <p className="text-sm text-gray-600">Send personalized reminder within 48 hours</p>
              </div>
            </div>
            
            <div className="flex items-start p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl border border-blue-200 hover:shadow-md transition-shadow">
              <span className="text-2xl mr-4">2️⃣</span>
              <div>
                <p className="font-bold text-gray-800">Follow-up Call</p>
                <p className="text-sm text-gray-600">Schedule call with account manager after 7 days</p>
              </div>
            </div>
            
            <div className="flex items-start p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200 hover:shadow-md transition-shadow">
              <span className="text-2xl mr-4">3️⃣</span>
              <div>
                <p className="font-bold text-gray-800">Escalation</p>
                <p className="text-sm text-gray-600">
                  {percentScore >= 70 
                    ? '✨ Unlikely needed - high recovery probability'
                    : '⚡ Consider DCA referral after 30 days'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 📈 SHAP Visualization Chart - Full Width */}
        <div className="bg-white rounded-2xl shadow-lg p-6 lg:col-span-2">
          <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="text-2xl mr-3">📈</span>
            Feature Impact Visualization
          </h2>
          <ShapChart factors={topFactors} />
          <p className="text-sm text-gray-500 text-center mt-4">
            🟢 Green = Positive impact on recovery | 🔴 Red = Negative impact
          </p>
        </div>
      </div>

      {/* Footer Timestamp */}
      <div className="text-center mt-8 text-sm text-gray-400">
        Analysis generated at: {account?.prediction_timestamp || new Date().toISOString()}
      </div>
    </div>
  )
}

export default AccountDetail