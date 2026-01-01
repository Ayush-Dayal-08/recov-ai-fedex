function AccountDetail({ accountId, onBack }) {
  return (
    <div>
      {/* Back Button */}
      <button
        onClick={onBack}
        className="mb-6 flex items-center text-fedex-purple hover: text-fedex-orange transition-colors"
      >
        <span className="mr-2">←</span>
        Back to Account List
      </button>

      {/* Placeholder for Day 5 */}
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Account Detail:  {accountId}
        </h2>
        <p className="text-gray-500">
          🚧 Full detail view coming in Day 5! 
        </p>
      </div>
    </div>
  )
}

export default AccountDetail