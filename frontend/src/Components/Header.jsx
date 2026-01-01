function Header({ onLogoClick }) {
  return (
    <header className="bg-fedex-purple text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 
            onClick={onLogoClick}
            className="text-2xl font-bold cursor-pointer hover:text-fedex-orange transition-colors"
          >
            🔮 RECOV.AI
          </h1>
          <p className="text-sm text-purple-200">
            AI-Powered Debt Recovery | FedEx SMART Hackathon
          </p>
        </div>
      </div>
    </header>
  )
}

export default Header