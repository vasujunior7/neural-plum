import { useState } from "react"
import { motion } from "framer-motion"
import { Card } from "../components/ui/Card"
import { Button } from "../components/ui/Button"
import { submitClaim } from "../utils/api"
import { useNavigate } from "react-router-dom"
import { UploadCloud, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react"

export function ClaimSubmission() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  
  const [memberId, setMemberId] = useState("")
  const [category, setCategory] = useState("CONSULTATION")
  const [amount, setAmount] = useState("")
  const [files, setFiles] = useState<File[]>([])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      if (files.length === 0) {
        throw new Error("Please upload at least one document.")
      }

      const formData = new FormData()
      formData.append("member_id", memberId)
      formData.append("claim_category", category)
      formData.append("claimed_amount", amount)
      
      files.forEach((file) => {
        formData.append("documents", file)
      })

      const result = await submitClaim(formData)
      setSuccess(true)
      
      // Navigate to claim detail after a short delay
      setTimeout(() => {
        navigate(`/claims/${result.claim_id}`)
      }, 1500)
      
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-4 md:p-8 space-y-8">
      <header className="flex flex-col gap-4">
        <button 
          onClick={() => navigate('/')} 
          className="flex items-center gap-2 text-text-secondary hover:text-primary transition-colors text-sm w-fit"
        >
          <ArrowLeft size={16} /> Back to Command Center
        </button>
        <div>
          <h1 className="text-3xl font-bold text-primary tracking-tight">Submit New Claim</h1>
          <p className="text-text-secondary mt-1 text-sm">Upload documents to auto-adjudicate a claim.</p>
        </div>
      </header>

      <Card className="p-8">
        {success ? (
          <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 20 }}
            >
              <CheckCircle size={64} className="text-status-success mb-2" />
            </motion.div>
            <h2 className="text-2xl font-bold text-primary">Claim Submitted</h2>
            <p className="text-text-secondary">Redirecting to claim review...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-4 bg-status-error_bg border border-status-error/20 rounded-md flex items-start gap-3 text-status-error">
                <AlertCircle size={20} className="shrink-0 mt-0.5" />
                <p className="text-sm font-medium">{error}</p>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-primary">Member ID</label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g. EMP-001"
                  className="industrial-input"
                  value={memberId}
                  onChange={e => setMemberId(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <label className="block text-sm font-medium text-primary">Claim Amount (₹)</label>
                <input 
                  type="number" 
                  required
                  min="1"
                  placeholder="e.g. 1500"
                  className="industrial-input"
                  value={amount}
                  onChange={e => setAmount(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-primary">Category</label>
              <select 
                className="industrial-input"
                value={category}
                onChange={e => setCategory(e.target.value)}
              >
                <option value="CONSULTATION">Consultation</option>
                <option value="HOSPITALIZATION">Hospitalization</option>
                <option value="PHARMACY">Pharmacy</option>
                <option value="DIAGNOSTICS">Diagnostics</option>
                <option value="DENTAL">Dental</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-primary">Documents</label>
              <div className="bg-slate-50 rounded-md p-8 border-dashed border-2 border-slate-300 flex flex-col items-center justify-center text-center space-y-4 hover:border-secondary transition-colors cursor-pointer" onClick={() => document.getElementById('file-upload')?.click()}>
                <UploadCloud size={40} className="text-slate-400" />
                <div>
                  <p className="text-text-primary text-sm font-medium">Click to upload or drag and drop</p>
                  <p className="text-text-muted text-xs mt-1">PDF, JPG, PNG up to 10MB each</p>
                </div>
                <input 
                  type="file" 
                  multiple 
                  className="hidden" 
                  id="file-upload"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={handleFileChange}
                />
                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    document.getElementById('file-upload')?.click();
                  }}
                >
                  Select Files
                </Button>
                {files.length > 0 && (
                  <div className="w-full mt-4 text-left">
                    <p className="text-xs font-medium text-primary mb-2">Selected files:</p>
                    <ul className="text-xs text-text-secondary space-y-1 pl-4 list-disc">
                      {files.map((file, i) => (
                        <li key={i}>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <Button type="submit" variant="primary" disabled={loading} className="w-full md:w-auto">
                {loading ? "Processing..." : "Submit Claim"}
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  )
}

