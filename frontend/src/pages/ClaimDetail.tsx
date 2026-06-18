import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Card } from "../components/ui/Card"
import { Badge } from "../components/ui/Badge"
import { Button } from "../components/ui/Button"
import { fetchClaim } from "../utils/api"
import { ArrowLeft, FileText, Activity, ShieldAlert, CheckCircle, XCircle, AlertCircle, Zap, Brain, ClipboardCheck, Eye, AlertTriangle, Shield, ChevronDown, ChevronUp } from "lucide-react"

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100)
  const color = confidence >= 0.8 ? 'text-status-success' : confidence >= 0.6 ? 'text-yellow-500' : 'text-status-error'
  const bg = confidence >= 0.8 ? 'bg-emerald-50' : confidence >= 0.6 ? 'bg-yellow-50' : 'bg-red-50'
  const icon = confidence >= 0.8 ? <CheckCircle size={12} /> : confidence >= 0.6 ? <AlertTriangle size={12} /> : <XCircle size={12} />
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-mono font-medium ${color} ${bg}`}>
      {icon} {pct}%
    </span>
  )
}

export function ClaimDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [claim, setClaim] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [rationaleOpen, setRationaleOpen] = useState(false)
  const [fraudOpen, setFraudOpen] = useState(false)
  const [checklistOpen, setChecklistOpen] = useState(true)

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

  const rationale = claim.rationale || []
  const fieldConfidences = claim.field_confidences || {}
  const semanticFraud = claim.semantic_fraud_result || {}
  const claimPlan = claim.claim_plan || {}
  const handlerChecklist = claim.handler_checklist

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

      {/* Phase 4: Claim Classification Banner */}
      {claimPlan.claim_category && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="p-4" style={{ background: 'linear-gradient(135deg, #f0f9ff 0%, #e8f4fd 100%)' }}>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Brain size={20} className="text-primary" />
                </div>
                <div>
                  <p className="text-xs text-text-muted uppercase tracking-wider font-semibold">Claim Classification</p>
                  <p className="text-sm font-bold text-text-primary">{claimPlan.claim_category}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                {claimPlan.fast_track && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700">
                    <Zap size={12} /> Fast Track
                  </span>
                )}
                <div className="text-center">
                  <p className="text-xs text-text-muted">Complexity</p>
                  <p className="text-sm font-mono font-bold text-primary">{((claimPlan.complexity_score || 0) * 100).toFixed(0)}%</p>
                </div>
                {claimPlan.agents_to_skip && Object.keys(claimPlan.agents_to_skip).length > 0 && (
                  <div className="text-xs text-text-secondary">
                    <p className="font-semibold text-text-muted">Skipped:</p>
                    {Object.entries(claimPlan.agents_to_skip).map(([agent, reason]: [string, any]) => (
                      <p key={agent} className="truncate max-w-[200px]" title={String(reason)}>{agent}: {String(reason)}</p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Phase 5: Claimant Summary Card */}
      {claim.human_summary && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="p-5 border-l-4" style={{ borderLeftColor: claim.decision === 'APPROVED' ? '#10b981' : claim.decision === 'REJECTED' ? '#ef4444' : claim.decision === 'MANUAL_REVIEW' ? '#f59e0b' : '#6366f1' }}>
            <h3 className="text-sm font-semibold text-primary flex items-center gap-2 mb-3">
              <Eye size={16} /> Summary for Claimant
            </h3>
            <div className="text-sm text-text-primary leading-relaxed whitespace-pre-line">
              {claim.human_summary}
            </div>
          </Card>
        </motion.div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column: Details, Confidence & Extracted Info */}
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
            
            {/* Phase 2: Confidence-Annotated Extraction */}
            <h3 className="text-sm font-semibold text-primary flex items-center gap-2 pt-4">
              <Activity size={16} /> Extracted Data
            </h3>
            <div className="space-y-3">
              {Object.keys(fieldConfidences).length > 0 ? (
                Object.entries(fieldConfidences).map(([key, data]: [string, any]) => (
                  <div key={key} className="text-sm">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-text-muted text-xs uppercase tracking-wider font-mono">{key.replace(/_/g, ' ')}</span>
                      <ConfidenceBadge confidence={data.confidence || 0} />
                    </div>
                    <span className="text-text-primary break-words font-medium text-sm">
                      {data.value !== null && data.value !== undefined ? String(data.value) : '—'}
                    </span>
                  </div>
                ))
              ) : (
                Object.entries(claim.extracted_data || {}).map(([key, value]: [string, any]) => (
                  <div key={key} className="text-sm">
                    <span className="block text-text-muted text-xs uppercase tracking-wider font-mono mb-1">{key.replace(/_/g, ' ')}</span>
                    <span className="text-text-primary break-words font-medium">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Phase 3: Fraud Analysis Panel */}
          {semanticFraud.fraud_score !== undefined && (
            <Card className="p-5 space-y-3">
              <button 
                onClick={() => setFraudOpen(!fraudOpen)} 
                className="w-full flex items-center justify-between text-sm font-semibold text-primary"
              >
                <span className="flex items-center gap-2">
                  <Shield size={16} /> Fraud Analysis
                </span>
                {fraudOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>
              
              {/* Score meter */}
              <div className="flex items-center gap-3">
                <div className="flex-1 h-2 rounded-full bg-slate-200 overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-500 ${
                      semanticFraud.fraud_score < 0.3 ? 'bg-emerald-500' : 
                      semanticFraud.fraud_score < 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${(semanticFraud.fraud_score || 0) * 100}%` }}
                  />
                </div>
                <span className={`text-sm font-mono font-bold ${
                  semanticFraud.fraud_score < 0.3 ? 'text-emerald-600' : 
                  semanticFraud.fraud_score < 0.7 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {((semanticFraud.fraud_score || 0) * 100).toFixed(0)}%
                </span>
              </div>
              
              {fraudOpen && semanticFraud.flags && semanticFraud.flags.length > 0 && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="space-y-2 pt-2">
                  {semanticFraud.flags.map((flag: any, idx: number) => (
                    <div key={idx} className="text-xs p-2 rounded-md border border-slate-200 bg-slate-50">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant={flag.severity === 'high' ? 'error' : flag.severity === 'medium' ? 'warning' : 'default'}>
                          {flag.severity}
                        </Badge>
                      </div>
                      <p className="text-text-secondary">{flag.signal}</p>
                      {flag.fields_involved && flag.fields_involved.length > 0 && (
                        <p className="text-text-muted mt-1">Fields: {flag.fields_involved.join(', ')}</p>
                      )}
                    </div>
                  ))}
                </motion.div>
              )}
              {fraudOpen && (!semanticFraud.flags || semanticFraud.flags.length === 0) && (
                <p className="text-xs text-text-secondary pt-1">No significant anomalies detected.</p>
              )}
            </Card>
          )}
        </div>

        {/* Right Column: Explainability Trace */}
        <div className="md:col-span-2 space-y-6">

          {/* Phase 1: Decision Breakdown Panel */}
          {rationale.length > 0 && (
            <Card className="p-0 overflow-hidden">
              <button 
                onClick={() => setRationaleOpen(!rationaleOpen)}
                className="w-full px-5 py-3 border-b border-border bg-gradient-to-r from-indigo-50 to-slate-50 flex items-center justify-between"
              >
                <div>
                  <h3 className="text-sm font-semibold text-primary">Decision Breakdown</h3>
                  <p className="text-xs text-text-secondary mt-0.5">{rationale.length} rule{rationale.length !== 1 ? 's' : ''} evaluated with policy references</p>
                </div>
                {rationaleOpen ? <ChevronUp size={16} className="text-text-secondary" /> : <ChevronDown size={16} className="text-text-secondary" />}
              </button>
              
              {rationaleOpen && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-5 space-y-3">
                  {rationale.map((r: any, idx: number) => (
                    <div key={idx} className="p-3 rounded-lg border border-slate-200 bg-white space-y-2">
                      <div className="flex items-start justify-between gap-2 flex-wrap">
                        <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 text-primary font-semibold">{r.rule_triggered}</span>
                        <span className="text-xs text-indigo-600 font-mono bg-indigo-50 px-2 py-0.5 rounded">{r.policy_reference}</span>
                      </div>
                      <div className="flex gap-4 text-xs">
                        <div>
                          <span className="text-text-muted">Computed:</span>{' '}
                          <span className="font-medium text-text-primary">{r.computed_value}</span>
                        </div>
                        <div>
                          <span className="text-text-muted">Threshold:</span>{' '}
                          <span className="font-medium text-text-primary">{r.threshold_value}</span>
                        </div>
                      </div>
                      <p className="text-sm text-text-secondary leading-relaxed">{r.human_explanation}</p>
                    </div>
                  ))}
                </motion.div>
              )}
            </Card>
          )}

          {/* Existing: Explainability Trace */}
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

          {/* Phase 6: Handler Checklist */}
          {handlerChecklist && handlerChecklist.items && handlerChecklist.items.length > 0 && (
            <Card className="p-0 overflow-hidden border-2 border-amber-200">
              <button
                onClick={() => setChecklistOpen(!checklistOpen)}
                className="w-full px-5 py-3 border-b border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 flex items-center justify-between"
              >
                <div className="flex items-center gap-2">
                  <ClipboardCheck size={16} className="text-amber-600" />
                  <div className="text-left">
                    <h3 className="text-sm font-semibold text-amber-800">Handler Checklist</h3>
                    <p className="text-xs text-amber-600">{handlerChecklist.items.length} items • Est. {handlerChecklist.total_estimated_minutes} min</p>
                  </div>
                </div>
                {checklistOpen ? <ChevronUp size={16} className="text-amber-600" /> : <ChevronDown size={16} className="text-amber-600" />}
              </button>
              
              {checklistOpen && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-5 space-y-3">
                  {handlerChecklist.items.map((item: any, idx: number) => (
                    <div key={idx} className="flex gap-3 p-3 rounded-md border border-amber-100 bg-amber-50/50">
                      <div className="w-6 h-6 rounded-full bg-amber-200 flex items-center justify-center text-xs font-bold text-amber-800 shrink-0">
                        {item.priority}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-text-primary">{item.action}</p>
                        <p className="text-xs text-text-secondary mt-1">{item.reason}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-xs text-text-muted font-mono">{item.source_agent}</span>
                          <span className="text-xs text-text-muted">~{item.estimated_minutes} min</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </motion.div>
              )}
            </Card>
          )}
        </div>

      </div>
    </div>
  )
}
