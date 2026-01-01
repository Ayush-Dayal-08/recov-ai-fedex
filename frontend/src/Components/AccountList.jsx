function AccountList({ accounts, onAccountClick }) {
  // Sort accounts by recovery probability (highest first)
  const sortedAccounts = [...accounts].sort((a, b) => {
    // Backend returns flat data, so we check recovery_probability directly
    const scoreA = a.recovery_probability || 0
    const scoreB = b.recovery_probability || 0
    return scoreB - scoreA
  })

  // Color coding function
  const getScoreColor = (probability) => {
    const percent = probability * 100
    if (percent >= 70) return 'bg-green-500'
    if (percent >= 50) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getScoreBgColor = (probability) => {
    const percent = probability * 100
    if (percent >= 70) return 'bg-green-50 border-green-200'
    if (percent >= 50) return 'bg-yellow-50 border-yellow-200'
    return 'bg-red-50 border-red-200'
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          📋 Account Analysis Results
        </h2>
        <p className="text-gray-500">
          {accounts.length} accounts analyzed • Sorted by recovery probability
        </p>
      </div>

      {/* Responsive Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sortedAccounts.map((account) => {
          const probability = account.recovery_probability || 0
          const percentScore = Math.round(probability * 100)
          
          return (
            <div
              key={account.account_id}
              onClick={() => onAccountClick(account.account_id)}
              className={`
                p-5 rounded-xl border-2 cursor-pointer
                transition-all duration-200 hover:shadow-lg hover:scale-[1.02]
                ${getScoreBgColor(probability)}
              `}
            >
              {/* Company Name */}
              <h3 className="text-lg font-bold text-gray-800 mb-3">
                🏢 {account.company_name}
              </h3>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Amount</p>
                  <p className="text-lg font-semibold text-gray-800">
                    {formatCurrency(account.amount)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Days Overdue</p>
                  <p className="text-lg font-semibold text-gray-800">
                    {account.days_overdue} days
                  </p>
                </div>
              </div>

              {/* Score Bar */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Recovery Score</p>
                  <p className="text-lg font-bold">{percentScore}%</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-500 ${getScoreColor(probability)}`}
                    style={{ width: `${percentScore}%` }}
                  ></div>
                </div>
              </div>

              {/* Click hint */}
              <p className="text-xs text-gray-400 mt-3 text-center">
                Click for details →
              </p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default AccountList