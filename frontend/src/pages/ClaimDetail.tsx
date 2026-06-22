import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { motion } from "framer-motion"
import { Card } from "../components/ui/Card"
import { Badge } from "../components/ui/Badge"
import { Button } from "../components/ui/Button"
import { fetchClaim } from "../utils/api"
import { 
  ArrowLeft, FileText, Activity, ShieldAlert, CheckCircle, 
  XCircle, AlertCircle, Zap, Brain, ClipboardCheck, 
  MessageSquare, Shield, ChevronDown, ChevronUp 
} from "lucide-react"

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100)
  const isHigh = confidence >= 0.8
  const isMed = confidence >= 0.6
  
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium ${
      isHigh ? 'text-emerald-700 bg-emerald-50 border border-emerald-200' : 
      isMed ? 'text-amber-700 bg-amber-50 border border-amber-200' : 
      'text-red-700 bg-red-50 border border-red-200'
    }`}>
      {pct}%
    </span>
  )
}

export function ClaimDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [claim, setClaim] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Accordion states
  const [rationaleOpen, setRationaleOpen] = useState(false)
  const [fraudOpen, setFraudOpen] = useState(false)

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
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <p className="text-sm text-text-muted">Loading claim record...</p>
        </div>
      </div>
    )
  }

  if (error || !claim) {
    return (
      <div className="max-w-2xl mx-auto mt-12 p-6">
        <Card className="text-center p-12 border-red-100 bg-red-50/30">
          <ShieldAlert size={32} className="mx-auto text-red-500 mb-4" />
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Record Not Found</h2>
          <p className="text-sm text-gray-500 mb-6">{error || 'The requested claim could not be retrieved.'}</p>
          <Button onClick={() => navigate('/')} variant="outline" className="bg-white">Return to Dashboard</Button>
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
    <div className="max-w-[1100px] mx-auto p-4 md:p-8 space-y-8 animate-in fade-in duration-500">
      
      {/* Header */}
      <header className="flex flex-col gap-4">
        <button 
          onClick={() => navigate('/')} 
          className="flex items-center gap-2 text-text-muted hover:text-primary transition-colors text-sm w-fit group"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> 
          Back to Command Center
        </button>
        
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-border pb-6 gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-gray-900">Claim #{claim.id}</h1>
              <Badge variant={
                claim.decision === 'APPROVED' ? 'success' : 
                claim.decision === 'REJECTED' ? 'error' : 
                claim.decision === 'MANUAL_REVIEW' ? 'warning' : 'default'
              }>
                {claim.decision ? claim.decision.replace('_', ' ') : claim.status}
              </Badge>
              {claimPlan.fast_track && (
                <Badge className="bg-blue-50 text-blue-700 border-blue-200">
                  <Zap size={10} className="mr-1" /> Fast Tracked
                </Badge>
              )}
            </div>
            <p className="text-sm text-gray-500">Patient: <span className="font-medium text-gray-700">{claim.member_id}</span> • {claim.claim_category}</p>
          </div>
          
          <div className="flex items-center gap-6 text-right">
            <div>
              <p className="text-[11px] font-medium text-gray-400 uppercase tracking-wider mb-1">AI Confidence</p>
              <p className="text-2xl font-mono text-gray-900">
                {claim.confidence !== undefined && claim.confidence !== null ? `${(claim.confidence * 100).toFixed(1)}%` : '-'}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Data & Insights (Span 5) */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Summary / Verdict */}
          {claim.human_summary && (
            <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
              <h3 className="text-[13px] font-semibold text-gray-900 flex items-center gap-2 mb-2">
                <MessageSquare size={14} className="text-gray-500" /> Executive Summary
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {claim.human_summary}
              </p>
            </div>
          )}

          {/* Financials */}
          <Card className="p-0 overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100 bg-white">
              <h3 className="text-[13px] font-semibold text-gray-900 flex items-center gap-2">
                <FileText size={14} className="text-gray-500" /> Financial Settlement
              </h3>
            </div>
            <div className="p-5 flex flex-col gap-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">Claimed Amount</span>
                <span className="font-mono text-sm text-gray-900">₹{claim.claimed_amount?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between items-center pt-3 border-t border-gray-100">
                <span className="text-sm font-medium text-gray-900">Approved Amount</span>
                <span className={`font-mono text-lg font-bold ${claim.approved_amount > 0 ? 'text-emerald-600' : 'text-gray-400'}`}>
                  ₹{claim.approved_amount?.toLocaleString() || 0}
                </span>
              </div>
            </div>
          </Card>
          
          {/* Fraud Analysis */}
          {semanticFraud.fraud_score !== undefined && (
            <Card className="p-0 overflow-hidden">
              <button 
                onClick={() => setFraudOpen(!fraudOpen)}
                className="w-full px-5 py-3 border-b border-gray-100 bg-white flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Shield size={14} className={semanticFraud.fraud_score > 0.5 ? 'text-red-500' : 'text-emerald-500'} />
                  <h3 className="text-[13px] font-semibold text-gray-900">Risk Assessment</h3>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-mono font-medium px-2 py-0.5 rounded ${
                    semanticFraud.fraud_score < 0.3 ? 'bg-emerald-50 text-emerald-700' : 
                    semanticFraud.fraud_score < 0.7 ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-700'
                  }`}>
                    {((semanticFraud.fraud_score || 0) * 100).toFixed(0)}% Risk
                  </span>
                  {fraudOpen ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
                </div>
              </button>
              
              {fraudOpen && semanticFraud.flags && semanticFraud.flags.length > 0 && (
                <div className="p-5 space-y-4 bg-gray-50/50">
                  {semanticFraud.flags.map((flag: any, idx: number) => (
                    <div key={idx} className="flex gap-3">
                      <div className="mt-0.5">
                        <AlertCircle size={14} className={flag.severity === 'high' ? 'text-red-500' : 'text-amber-500'} />
                      </div>
                      <div>
                        <p className="text-sm text-gray-700">{flag.signal}</p>
                        {flag.fields_involved && flag.fields_involved.length > 0 && (
                          <p className="text-[11px] text-gray-500 font-mono mt-1">Fields: {flag.fields_involved.join(', ')}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {fraudOpen && (!semanticFraud.flags || semanticFraud.flags.length === 0) && (
                <div className="p-5 bg-gray-50/50 text-sm text-gray-500 text-center">
                  No anomalous patterns detected.
                </div>
              )}
            </Card>
          )}

          {/* Extracted Data */}
          <Card className="p-0 overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-100 bg-white">
              <h3 className="text-[13px] font-semibold text-gray-900 flex items-center gap-2">
                <Activity size={14} className="text-gray-500" /> OCR Extraction
              </h3>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-1 gap-4">
                {Object.keys(fieldConfidences).length > 0 ? (
                  Object.entries(fieldConfidences).map(([key, data]: [string, any]) => (
                    <div key={key} className="flex flex-col">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] text-gray-500 uppercase tracking-wider font-medium">{key.replace(/_/g, ' ')}</span>
                        <ConfidenceBadge confidence={data.confidence || 0} />
                      </div>
                      <span className="text-sm text-gray-900 font-medium">
                        {data.value !== null && data.value !== undefined ? String(data.value) : '—'}
                      </span>
                    </div>
                  ))
                ) : (
                  Object.entries(claim.extracted_data || {}).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex flex-col">
                      <span className="text-[11px] text-gray-500 uppercase tracking-wider font-medium mb-1">{key.replace(/_/g, ' ')}</span>
                      <span className="text-sm text-gray-900 font-medium">
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column: Processing Pipeline & Reasoning (Span 7) */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Explainability Timeline */}
          <Card className="p-0 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 bg-white">
              <h3 className="text-[13px] font-semibold text-gray-900 flex items-center gap-2">
                <Brain size={14} className="text-gray-500" /> Adjudication Pipeline
              </h3>
            </div>
            
            <div className="p-6">
              {/* Vertical Timeline */}
              <div className="relative border-l border-gray-200 ml-3 space-y-8 pb-4">
                
                {/* Render Trace Steps */}
                {claim.trace && claim.trace.map((step: any, index: number) => {
                  const isPass = step.status === 'PASS'
                  const isFail = step.status === 'FAIL'
                  
                  return (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      key={index} 
                      className="relative pl-6"
                    >
                      {/* Timeline Dot */}
                      <span className={`absolute -left-2.5 top-1 flex h-5 w-5 items-center justify-center rounded-full bg-white border-2 ${
                        isPass ? 'border-emerald-500' : isFail ? 'border-red-500' : 'border-blue-500'
                      }`}>
                        {isPass ? <CheckCircle size={10} className="text-emerald-500" /> : 
                         isFail ? <XCircle size={10} className="text-red-500" /> : 
                         <div className="h-1.5 w-1.5 rounded-full bg-blue-500" />}
                      </span>
                      
                      <div className="flex flex-col">
                        <span className="text-sm font-semibold text-gray-900">{step.step}</span>
                        <span className="text-sm text-gray-500 mt-1 leading-relaxed">{step.message}</span>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </Card>

          {/* Rationale / Policy Breakdown */}
          {rationale.length > 0 && (
            <Card className="p-0 overflow-hidden">
              <button 
                onClick={() => setRationaleOpen(!rationaleOpen)}
                className="w-full px-6 py-4 border-b border-gray-100 bg-white flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div>
                  <h3 className="text-[13px] font-semibold text-gray-900 text-left flex items-center gap-2">
                    Policy Rules Applied
                  </h3>
                  <p className="text-[11px] text-gray-500 mt-0.5">{rationale.length} rule{rationale.length !== 1 ? 's' : ''} evaluated</p>
                </div>
                {rationaleOpen ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
              </button>
              
              {rationaleOpen && (
                <div className="p-6 bg-gray-50/30 space-y-4">
                  {rationale.map((r: any, idx: number) => (
                    <div key={idx} className="p-4 rounded-lg border border-gray-200 bg-white space-y-3">
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-2">
                        <span className="text-xs font-semibold text-gray-900">{r.rule_triggered}</span>
                        <span className="text-[10px] text-blue-600 font-mono bg-blue-50 px-2 py-0.5 rounded border border-blue-100">{r.policy_reference}</span>
                      </div>
                      <p className="text-sm text-gray-600 leading-relaxed">{r.human_explanation}</p>
                      
                      <div className="flex gap-6 pt-2">
                        <div className="flex flex-col">
                          <span className="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Computed</span>
                          <span className="font-mono text-sm text-gray-800">{r.computed_value}</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Threshold</span>
                          <span className="font-mono text-sm text-gray-800">{r.threshold_value}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}

          {/* Actionable Checklist */}
          {handlerChecklist && handlerChecklist.items && handlerChecklist.items.length > 0 && (
            <Card className="p-0 overflow-hidden border-indigo-100">
              <div className="px-6 py-4 border-b border-indigo-50 bg-indigo-50/30 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ClipboardCheck size={16} className="text-indigo-600" />
                  <div className="text-left">
                    <h3 className="text-[13px] font-semibold text-indigo-900">Required Actions</h3>
                  </div>
                </div>
                <span className="text-xs font-medium text-indigo-600 bg-indigo-100 px-2 py-1 rounded">
                  {handlerChecklist.total_estimated_minutes} min est.
                </span>
              </div>
              
              <div className="p-0">
                {handlerChecklist.items.map((item: any, idx: number) => (
                  <div key={idx} className="flex gap-4 p-4 border-b border-gray-100 last:border-0 hover:bg-gray-50 transition-colors">
                    <div className="mt-0.5">
                      <div className="w-4 h-4 rounded border-2 border-gray-300 bg-white" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{item.action}</p>
                      <p className="text-sm text-gray-500 mt-1">{item.reason}</p>
                      <div className="flex items-center gap-3 mt-2">
                        <span className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">{item.source_agent}</span>
                        <span className="text-[10px] text-gray-400 font-mono px-1.5 py-0.5 bg-gray-100 rounded">{item.estimated_minutes}m</span>
                        <span className="text-[10px] text-gray-400 font-mono px-1.5 py-0.5 bg-gray-100 rounded">{item.priority}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

        </div>
      </div>
    </div>
  )
}
