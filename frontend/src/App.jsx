import { useState } from 'react'
import Header from './components/Header'
import FileUpload from './components/FileUpload'
import AccountList from './components/AccountList'
import AccountDetail from './components/AccountDetail'

function App() {
  // Simple state-based routing (no react-router needed!)
  const [currentView, setCurrentView] = useState('upload') // 'upload', 'list', 'detail'
  const [accounts, setAccounts] = useState([])
  const [selectedAccountId, setSelectedAccountId] = useState(null)

  const handleUploadSuccess = (data) => {
    setAccounts(data.predictions || [])
    setCurrentView('list')
  }

  const handleAccountClick = (accountId) => {
    setSelectedAccountId(accountId)
    setCurrentView('detail')
    // Update URL for demo purposes
    window.history.pushState({}, '', `/account/${accountId}`)
  }

  const handleBackToList = () => {
    setCurrentView('list')
    window.history.pushState({}, '', '/')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onLogoClick={() => { setCurrentView('upload'); window.history.pushState({}, '', '/') }} />
      
      <main className="container mx-auto px-4 py-8">
        {currentView === 'upload' && (
          <FileUpload onSuccess={handleUploadSuccess} />
        )}
        
        {currentView === 'list' && (
          <AccountList 
            accounts={accounts} 
            onAccountClick={handleAccountClick} 
          />
        )}
        
        {currentView === 'detail' && (
          <AccountDetail 
            accountId={selectedAccountId}
            onBack={handleBackToList}
          />
        )}
      </main>
    </div>
  )
}

export default App