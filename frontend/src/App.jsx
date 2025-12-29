import { useState } from 'react'
import './App.css'

function App() {
  // 1. STATE: This holds the form data
  const [formData, setFormData] = useState({
    amount: 5000,
    days_overdue: 10,
    payment_history_score: 0.8,
    shipment_volume_change_30d: 0.0,
    email_opened: 1,
    dispute_flag: 0
  })
  
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // 2. HANDLE INPUT CHANGES
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  // 3. SEND DATA TO AI BACKEND
  const scanClient = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      alert("Error connecting to AI: " + error)
    }
    setLoading(false)
  }

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial', maxWidth: '800px', margin: '0 auto' }}>
      
      {/* HEADER */}
      <h1 style={{ color: '#4D148C' }}>🟣 RECOV.AI <span style={{fontSize:'18px', color:'#666'}}>FedEx Edition</span></h1>
      <p>AI-Powered Debt Recovery & Risk Scanner</p>
      <hr />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        
        {/* FORM LEFT */}
        <div style={{ background: '#f5f5f5', padding: '20px', borderRadius: '10px' }}>
          <h3>📋 Client Data</h3>
          
          <label>Invoice Amount ($)</label>
          <input type="number" name="amount" value={formData.amount} onChange={handleChange} style={inputStyle} />

          <label>Days Overdue</label>
          <input type="number" name="days_overdue" value={formData.days_overdue} onChange={handleChange} style={inputStyle} />

          <label>Shipment Volume Change (-1.0 to 1.0)</label>
          <p style={{fontSize:'12px', color:'gray'}}>*Key Indicator: Increase = Good, Decrease = Bad</p>
          <input type="number" name="shipment_volume_change_30d" step="0.1" value={formData.shipment_volume_change_30d} onChange={handleChange} style={inputStyle} />
          
          <br/><br/>
          <button onClick={scanClient} style={buttonStyle} disabled={loading}>
            {loading ? "🤖 Scanning..." : "🚀 SCAN CLIENT RISK"}
          </button>
        </div>

        {/* RESULTS RIGHT */}
        <div style={{ border: '2px solid #eee', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
          <h3>🔍 AI Analysis Result</h3>
          
          {result ? (
            <div>
              <h1 style={{ color: result.prediction === 1 ? 'green' : 'red', fontSize: '40px' }}>
                {result.prediction === 1 ? "✅ WILL PAY" : "⚠️ HIGH RISK"}
              </h1>
              <p style={{ fontSize: '18px' }}>Confidence Score: <strong>{(1 - result.risk_score).toFixed(2) * 100}%</strong></p>
              <p>{result.message}</p>
              
              {result.prediction === 0 && (
                 <div style={{background: '#ffebee', padding:'10px', marginTop:'20px'}}>
                    <strong>💡 Recommendation:</strong><br/>
                    "Shipment volume is dropping. Stop credit immediately."
                 </div>
              )}
            </div>
          ) : (
            <p style={{color:'#999', marginTop:'50px'}}>Waiting for scan...</p>
          )}
        </div>

      </div>
    </div>
  )
}

// Simple CSS Styles
const inputStyle = { width: '100%', padding: '8px', marginBottom: '10px', borderRadius: '5px', border: '1px solid #ccc' }
const buttonStyle = { width: '100%', padding: '15px', background: '#FF6200', color: 'white', border: 'none', borderRadius: '5px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer' }

export default App