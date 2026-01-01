import { useState } from 'react'

function FileUpload({ onSuccess }) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [fileName, setFileName] = useState('')

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file')
      return
    }

    setFileName(file.name)
    setError(null)
    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('Upload success:', data)
      onSuccess(data)
    } catch (err) {
      console.error('Upload error:', err)
      setError(err.message || 'Failed to upload file. Is the backend running?')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2 text-center">
          📊 Upload Account Data
        </h2>
        <p className="text-gray-500 text-center mb-6">
          Upload your CSV file to analyze recovery probability
        </p>

        {/* File Input */}
        <label className="block">
          <div className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors duration-200
            ${isLoading 
              ? 'border-gray-300 bg-gray-50' 
              : 'border-fedex-purple hover:border-fedex-orange hover:bg-purple-50'}
          `}>
            {isLoading ? (
              <div className="flex flex-col items-center">
                {/* Loading Spinner */}
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-fedex-purple border-t-transparent mb-4"></div>
                <p className="text-fedex-purple font-medium">Analyzing {fileName}...</p>
                <p className="text-sm text-gray-500 mt-1">AI is processing your data</p>
              </div>
            ) : (
              <>
                <div className="text-4xl mb-4">📁</div>
                <p className="text-lg font-medium text-gray-700">
                  Click to select CSV file
                </p>
                <p className="text-sm text-gray-400 mt-2">
                  or drag and drop here
                </p>
              </>
            )}
          </div>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={isLoading}
            className="hidden"
          />
        </label>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm flex items-center">
              <span className="mr-2">❌</span>
              {error}
            </p>
          </div>
        )}

        {/* Help Text */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">
            <strong>💡 Tip:</strong> Use the demo CSV from your project's data folder
          </p>
        </div>
      </div>
    </div>
  )
}

export default FileUpload