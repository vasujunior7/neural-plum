import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Card } from "../components/ui/Card"
import { Badge } from "../components/ui/Badge"
import { Button } from "../components/ui/Button"
import { fetchClaim } from "../utils/api"
import { ArrowLeft, FileText, Activity, ShieldAlert, CheckCircle, XCircle } from "lucide-react"

export function ClaimDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [claim, setClaim] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadClaim = async () => {
      try {
        const data = await fetchClaim(id!)
        setClaim(data)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    loadClaim()
  }, [id])

  if (loading) {
    return <div className="flex justify-center p-12 text-primary">Loading...</div>
  }

  if (error || !claim) {
    return (
      <div className="max-w-3xl mx-auto p-8">
        <Card className="text-center space-y-4 p-8">
          <ShieldAlert size={48} className="mx-auto text-status-error" />
          <h2 className="text-xl font-bold text-status-error">Error Loading Claim</h2>
          <p className="text-text-secondary">{error}</p>
          <Button onClick={() => navigate('/')} variant="outline">Return to Dashboard</Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-8 space-y-6">
      <header className="flex flex-col gap-4">
        <button 
          onClick={() => navigate('/')} 
          className="flex items-center gap-2 text-text-secondary hover:text-primary transition-colors text-sm w-fit"
        >
          <ArrowLeft size={16} /> Back to Command Center
        </button>
        <div className="flex justify-between items-end border-b border-border pb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-primary tracking-tight">Claim #{claim.id}</h1>
              <Badge variant={
                claim.decision === 'APPROVED' ? 'success' : 
                claim.decision === 'REJECTED' ? 'error' : 
                claim.decision === 'MANUAL_REVIEW' ? 'warning' : 'default'
              }>
                {claim.decision ? claim.decision.replace('_', ' ') : claim.status}
              </Badge>
            </div>
            <p className="text-text-secondary text-sm">Patient: {claim.member_id} • {claim.claim_category}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-text-muted">Confidence</p>
            <p className="text-2xl font-mono text-primary font-bold">
              {claim.confidence !== undefined && claim.confidence !== null ? `${(claim.confidence * 100).toFixed(1)}%` : '-'}
            </p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column: Details & Extracted Info */}
        <div className="md:col-span-1 space-y-6">
          <Card className="space-y-4 p-5">
            <h3 className="text-sm font-semibold text-primary flex items-center gap-2">
              <FileText size={16} /> Financials
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <span className="text-text-secondary text-sm">Claimed</span>
                <span className="font-mono font-medium text-text-primary text-sm">₹{claim.claimed_amount}</span>
              </div>
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <span className="text-text-secondary text-sm">Approved</span>
                <span className="font-mono font-bold text-status-success text-sm">₹{claim.approved_amount}</span>
              </div>
            </div>
            
            <h3 className="text-sm font-semibold text-primary flex items-center gap-2 pt-4">
              <Activity size={16} /> Extracted Data
            </h3>
            <div className="space-y-3">
              {Object.entries(claim.extracted_data || {}).map(([key, value]) => (
                <div key={key} className="text-sm">
                  <span className="block text-text-muted text-xs uppercase tracking-wider font-mono mb-1">{key.replace(/_/g, ' ')}</span>
                  <span className="text-text-primary break-words font-medium">
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column: Explainability Trace */}
        <div className="md:col-span-2 space-y-6">
          <Card className="p-0 overflow-hidden">
            <div className="px-5 py-3 border-b border-border bg-slate-50">
              <h3 className="text-sm font-semibold text-primary">Explainability Trace</h3>
              <p className="text-xs text-text-secondary mt-1">Audit log of system checks and reasoning.</p>
            </div>
            
            <div className="p-5 space-y-4">
              {/* Decision Reason */}
              <div className="mb-6 p-4 rounded-md bg-slate-50 border border-slate-200">
                <h4 className="text-sm font-semibold text-primary mb-2">Final Reasoning</h4>
                <p className="text-text-secondary leading-relaxed text-sm">{claim.reason}</p>
              </div>

              {/* Trace Logs */}
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-primary mb-3">Verification Steps</h4>
                {claim.trace && claim.trace.map((step: any, index: number) => (
                  <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    key={index} 
                    className="flex gap-3 text-sm p-3 rounded-md border border-slate-200 bg-white shadow-sm"
                  >
                    <div className="mt-0.5 shrink-0">
                      {step.status === 'PASS' ? <CheckCircle size={16} className="text-status-success" /> : 
                       step.status === 'FAIL' ? <XCircle size={16} className="text-status-error" /> : 
                       <AlertCircle size={16} className="text-status-info" />}
                    </div>
                    <div>
                      <span className="font-semibold text-text-primary block mb-1 text-sm">{step.step}</span>
                      <span className="text-text-secondary text-sm">{step.message}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </Card>
        </div>

      </div>
    </div>
  )
}

