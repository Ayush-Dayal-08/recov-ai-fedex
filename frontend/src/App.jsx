import { useState } from 'react'
import './App.css'

function App() {
  // 1. STATE: Updated to match your Python Backend requirements exactly
  const [formData, setFormData] = useState({
    account_id: "ACC-001",
    company_name: "TechCorp Test",
    amount: 5000,
    days_overdue: 45,
    payment_history_score: 0.75,
    shipment_volume_30d: 120,
    shipment_volume_change_30d: 0.15,
    industry: "Technology",
    region: "North",
    email_opened: 1,
    dispute_flag: 0
  })
  
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // 2. HANDLE INPUT CHANGES
  const handleChange = (e) => {
    // Handle numbers correctly
    const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value
    setFormData({ ...formData, [e.target.name]: value })
  }

  // 3. SEND DATA TO AI BACKEND
  const scanClient = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // PERMANENT FIX: Points to port 8000 where FastAPI is running
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error(`Server Error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      console.error(err)
      setError("Failed to connect to AI. Is Backend running on Port 8000?")
    }
    setLoading(false)
  }

  return (
    <div style={{ padding: '40px', fontFamily: 'Arial', maxWidth: '1000px', margin: '0 auto' }}>
      
      {/* HEADER */}
      <h1 style={{ color: '#4D148C' }}>🟣 RECOV.AI <span style={{fontSize:'18px', color:'#666'}}>FedEx Edition</span></h1>
      <p>AI-Powered Debt Recovery & Risk Scanner</p>
      <hr />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginTop: '20px' }}>
        
        {/* FORM LEFT */}
        <div style={{ background: '#f5f5f5', padding: '25px', borderRadius: '12px' }}>
          <h3>📋 Client Data</h3>
          
          <label style={labelStyle}>Company Name</label>
          <input type="text" name="company_name" value={formData.company_name} onChange={handleChange} style={inputStyle} />

          <label style={labelStyle}>Invoice Amount ($)</label>
          <input type="number" name="amount" value={formData.amount} onChange={handleChange} style={inputStyle} />

          <label style={labelStyle}>Days Overdue</label>
          <input type="number" name="days_overdue" value={formData.days_overdue} onChange={handleChange} style={inputStyle} />

          <label style={labelStyle}>Shipment Volume Change (-1.0 to 1.0)</label>
          <p style={{fontSize:'12px', color:'gray', margin:'-5px 0 10px'}}>*Positive = Growing, Negative = Shrinking</p>
          <input type="number" name="shipment_volume_change_30d" step="0.1" value={formData.shipment_volume_change_30d} onChange={handleChange} style={inputStyle} />
          
          <br/><br/>
          <button onClick={scanClient} style={buttonStyle} disabled={loading}>
            {loading ? "🤖 AI Scanning..." : "🚀 SCAN CLIENT RISK"}
          </button>

          {error && <p style={{color: 'red', marginTop: '10px'}}>{error}</p>}
        </div>

        {/* RESULTS RIGHT */}
        <div style={{ border: '2px solid #eee', padding: '25px', borderRadius: '12px', minHeight: '400px' }}>
          <h3>🔍 AI Analysis Result</h3>
          
          {result ? (
            <div>
              {/* Risk Level Header */}
              <div style={{
                background: result.risk_level === 'High' ? '#ffebee' : '#e8f5e9',
                padding: '15px',
                borderRadius: '8px',
                textAlign: 'center',
                marginBottom: '20px'
              }}>
                <h2 style={{ 
                  color: result.risk_level === 'High' ? '#c62828' : '#2e7d32', 
                  margin: 0,
                  fontSize: '32px'
                }}>
                  {result.risk_level === 'High' ? "⚠️ HIGH RISK" : "✅ LOW RISK"}
                </h2>
                <p style={{margin: '5px 0 0 0', fontWeight: 'bold'}}>
                  Recovery Probability: {(result.recovery_probability * 100).toFixed(1)}%
                </p>
              </div>

              {/* Metrics Grid */}
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px'}}>
                <div style={cardStyle}>
                  <small>Expected Recovery</small>
                  <div style={{fontWeight:'bold', fontSize:'18px'}}>{(result.recovery_percentage * 100).toFixed(0)}%</div>
                </div>
                <div style={cardStyle}>
                  <small>Est. Days to Pay</small>
                  <div style={{fontWeight:'bold', fontSize:'18px'}}>{result.expected_days} Days</div>
                </div>
              </div>

              {/* Top Factors */}
              <div>
                <h4>🧠 Why this prediction? (SHAP Analysis)</h4>
                {result.top_factors && result.top_factors.map((factor, index) => (
                  <div key={index} style={{
                    display: 'flex', justifyContent: 'space-between', 
                    borderBottom: '1px solid #eee', padding: '8px 0'
                  }}>
                    <span>{factor.feature}</span>
                    <span style={{
                      color: factor.direction === 'positive' ? 'green' : 'red', 
                      fontWeight: 'bold'
                    }}>
                      {factor.direction === 'positive' ? '⬆ Increases Recovery' : '⬇ Increases Risk'}
                    </span>
                  </div>
                ))}
              </div>

              {/* Recommended Action */}
              <div style={{marginTop: '20px', padding: '10px', background: '#e3f2fd', borderRadius: '5px'}}>
                 <strong>💡 Strategy:</strong> {result.recommended_dca.name} ({result.recommended_dca.specialization})
              </div>

            </div>
          ) : (
            <div style={{textAlign: 'center', marginTop: '100px', color: '#ccc'}}>
              <p style={{fontSize: '50px', margin: 0}}>📊</p>
              <p>Enter client details and click Scan</p>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}

// Styles
const inputStyle = { width: '100%', padding: '10px', marginBottom: '15px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box' }
const labelStyle = { display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '14px' }
const buttonStyle = { width: '100%', padding: '15px', background: '#FF6200', color: 'white', border: 'none', borderRadius: '6px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer' }
const cardStyle = { background: '#f9f9f9', padding: '10px', borderRadius: '5px', textAlign: 'center' }

export default App