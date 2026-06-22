import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "../components/ui/Card"
import { Badge } from "../components/ui/Badge"
import { Button } from "../components/ui/Button"
import { fetchClaim } from "../utils/api"
import { 
  ArrowLeft, FileText, Activity, ShieldAlert, CheckCircle2, 
  XCircle, AlertCircle, Zap, BrainCircuit, ClipboardCheck, 
  MessageSquare, Shield, ChevronDown, ChevronUp, User, LayoutGrid
} from "lucide-react"

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100)
  const isHigh = confidence >= 0.8
  const isMed = confidence >= 0.6
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium ${
      isHigh ? 'text-emerald-700 bg-emerald-50 border border-emerald-200/60' : 
      isMed ? 'text-amber-700 bg-amber-50 border border-amber-200/60' : 
      'text-red-700 bg-red-50 border border-red-200/60'
    }`}>
      <span className={`w-1.5 h-1.5 rounded-full ${
        isHigh ? 'bg-emerald-500' : isMed ? 'bg-amber-500' : 'bg-red-500'
      }`} />
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
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 rounded-full border-2 border-slate-300 border-t-slate-800 animate-spin" />
          <p className="text-sm font-medium text-slate-500">Retrieving claim record...</p>
        </div>
      </div>
    )
  }

  if (error || !claim) {
    return (
      <div className="max-w-2xl mx-auto mt-16 p-6">
        <Card className="text-center p-12 border-slate-200 bg-slate-50/50 shadow-sm">
          <ShieldAlert size={40} className="mx-auto text-slate-400 mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Record Not Found</h2>
          <p className="text-sm text-slate-500 mb-8">{error || 'The requested claim could not be retrieved from the database.'}</p>
          <Button onClick={() => navigate('/')} variant="outline" className="bg-white hover:bg-slate-50 transition-colors">
            Return to Command Center
          </Button>
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
    <div className="max-w-[1200px] mx-auto p-4 md:p-8 space-y-8 animate-in fade-in duration-500 pb-20">
      
      {/* Header Area */}
      <header className="flex flex-col gap-6 relative">
        <button 
          onClick={() => navigate('/')} 
          className="flex items-center gap-2 text-slate-500 hover:text-slate-900 transition-colors text-sm font-medium w-fit group"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> 
          Back to Command Center
        </button>
        
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-slate-200 pb-6 gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Claim #{claim.id}</h1>
              <Badge variant={
                claim.decision === 'APPROVED' ? 'success' : 
                claim.decision === 'REJECTED' ? 'error' : 
                claim.decision === 'MANUAL_REVIEW' ? 'warning' : 'default'
              } className="px-3 py-1 text-xs uppercase tracking-widest font-semibold rounded-md shadow-sm">
                {claim.decision ? claim.decision.replace('_', ' ') : claim.status}
              </Badge>
              {claimPlan.fast_track && (
                <Badge className="bg-indigo-50 text-indigo-700 border-indigo-200/60 px-3 py-1 shadow-sm">
                  <Zap size={12} className="mr-1.5" /> Fast Tracked
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-4 text-sm text-slate-600">
              <div className="flex items-center gap-1.5">
                <User size={14} className="text-slate-400" />
                <span className="font-medium text-slate-900">{claim.member_id}</span>
              </div>
              <div className="w-1 h-1 rounded-full bg-slate-300" />
              <div className="flex items-center gap-1.5">
                <LayoutGrid size={14} className="text-slate-400" />
                <span>{claim.claim_category}</span>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col items-start md:items-end p-4 bg-white rounded-lg border border-slate-200 shadow-sm min-w-[200px]">
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-1">System Confidence</p>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-mono text-slate-900 tracking-tight">
                {claim.confidence !== undefined && claim.confidence !== null ? `${(claim.confidence * 100).toFixed(1)}%` : '-'}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Data & Context (Span 5) */}
        <div className="lg:col-span-5 space-y-6 sticky top-6">
          
          {/* Executive Summary */}
          {claim.human_summary && (
            <div className="bg-slate-900 rounded-xl p-6 shadow-md text-slate-50 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none" />
              <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2 mb-4 tracking-wide uppercase">
                <MessageSquare size={14} className="text-indigo-400" /> Executive Summary
              </h3>
              <p className="text-sm leading-relaxed whitespace-pre-wrap font-medium">
                {claim.human_summary}
              </p>
            </div>
          )}

          {/* Financial Settlement */}
          <Card className="p-0 overflow-hidden border-slate-200 shadow-sm rounded-xl">
            <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50">
              <h3 className="text-[13px] font-semibold text-slate-900 flex items-center gap-2 uppercase tracking-wide">
                <FileText size={14} className="text-slate-500" /> Financial Settlement
              </h3>
            </div>
            <div className="p-5 flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600">Claimed Amount</span>
                <span className="font-mono text-sm text-slate-900 font-medium">₹{claim.claimed_amount?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between items-center pt-4 border-t border-slate-100">
                <span className="text-sm font-semibold text-slate-900">Approved Amount</span>
                <span className={`font-mono text-xl font-bold ${claim.approved_amount > 0 ? 'text-emerald-600' : 'text-slate-400'}`}>
                  ₹{claim.approved_amount?.toLocaleString() || 0}
                </span>
              </div>
            </div>
          </Card>
          
          {/* Risk Assessment */}
          {semanticFraud.fraud_score !== undefined && (
            <Card className="p-0 overflow-hidden border-slate-200 shadow-sm rounded-xl">
              <button 
                onClick={() => setFraudOpen(!fraudOpen)}
                className="w-full px-5 py-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between hover:bg-slate-100 transition-colors group cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <Shield size={14} className={semanticFraud.fraud_score > 0.5 ? 'text-red-500' : 'text-emerald-500'} />
                  <h3 className="text-[13px] font-semibold text-slate-900 uppercase tracking-wide">Risk Assessment</h3>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-mono font-medium px-2.5 py-0.5 rounded-full border ${
                    semanticFraud.fraud_score < 0.3 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 
                    semanticFraud.fraud_score < 0.7 ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-red-50 text-red-700 border-red-200'
                  }`}>
                    {((semanticFraud.fraud_score || 0) * 100).toFixed(0)}% Risk
                  </span>
                  {fraudOpen ? <ChevronUp size={16} className="text-slate-400 group-hover:text-slate-600" /> : <ChevronDown size={16} className="text-slate-400 group-hover:text-slate-600" />}
                </div>
              </button>
              
              <AnimatePresence>
                {fraudOpen && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    {semanticFraud.flags && semanticFraud.flags.length > 0 ? (
                      <div className="p-5 space-y-4 bg-white">
                        {semanticFraud.flags.map((flag: any, idx: number) => (
                          <div key={idx} className="flex gap-3 p-3 rounded-lg border border-slate-100 bg-slate-50">
                            <div className="mt-0.5">
                              <AlertCircle size={14} className={flag.severity === 'high' ? 'text-red-500' : 'text-amber-500'} />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-slate-800">{flag.signal}</p>
                              {flag.fields_involved && flag.fields_involved.length > 0 && (
                                <p className="text-[11px] text-slate-500 font-mono mt-1.5 uppercase tracking-wider">Fields: {flag.fields_involved.join(', ')}</p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-6 bg-white text-sm text-slate-500 text-center flex flex-col items-center gap-2">
                        <CheckCircle2 size={24} className="text-emerald-400" />
                        No anomalous patterns detected in submission.
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </Card>
          )}

          {/* OCR Extraction Confidence */}
          <Card className="p-0 overflow-hidden border-slate-200 shadow-sm rounded-xl">
            <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50">
              <h3 className="text-[13px] font-semibold text-slate-900 flex items-center gap-2 uppercase tracking-wide">
                <Activity size={14} className="text-slate-500" /> Extraction Confidence
              </h3>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-1 gap-5">
                {Object.keys(fieldConfidences).length > 0 ? (
                  Object.entries(fieldConfidences).map(([key, data]: [string, any]) => (
                    <div key={key} className="flex flex-col gap-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] text-slate-500 uppercase tracking-widest font-semibold">{key.replace(/_/g, ' ')}</span>
                        <ConfidenceBadge confidence={data.confidence || 0} />
                      </div>
                      <span className="text-sm text-slate-900 font-medium bg-slate-50 p-2.5 rounded border border-slate-100">
                        {data.value !== null && data.value !== undefined ? String(data.value) : '—'}
                      </span>
                    </div>
                  ))
                ) : (
                  Object.entries(claim.extracted_data || {}).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex flex-col gap-1.5">
                      <span className="text-[11px] text-slate-500 uppercase tracking-widest font-semibold">{key.replace(/_/g, ' ')}</span>
                      <span className="text-sm text-slate-900 font-medium bg-slate-50 p-2.5 rounded border border-slate-100">
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
          
          {/* Adjudication Pipeline Timeline */}
          <Card className="p-0 overflow-hidden border-slate-200 shadow-sm rounded-xl">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
              <h3 className="text-[13px] font-semibold text-slate-900 flex items-center gap-2 uppercase tracking-wide">
                <BrainCircuit size={14} className="text-slate-500" /> System Trace
              </h3>
            </div>
            
            <div className="p-6 md:p-8">
              <div className="relative border-l border-slate-200 ml-4 space-y-8 pb-2">
                {claim.trace && claim.trace.map((step: any, index: number) => {
                  const isPass = step.status === 'PASS'
                  const isFail = step.status === 'FAIL'
                  
                  return (
                    <motion.div 
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      key={index} 
                      className="relative pl-8"
                    >
                      {/* Timeline Node */}
                      <span className={`absolute -left-3 top-1 flex h-6 w-6 items-center justify-center rounded-full bg-white border-2 shadow-sm ${
                        isPass ? 'border-emerald-500' : isFail ? 'border-red-500' : 'border-indigo-500'
                      }`}>
                        {isPass ? <CheckCircle2 size={12} className="text-emerald-500" /> : 
                         isFail ? <XCircle size={12} className="text-red-500" /> : 
                         <div className="h-2 w-2 rounded-full bg-indigo-500" />}
                      </span>
                      
                      <div className="flex flex-col bg-white rounded-lg border border-slate-100 p-4 shadow-sm hover:shadow-md transition-shadow">
                        <span className="text-[11px] uppercase tracking-widest font-bold text-slate-500 mb-1">{step.step}</span>
                        <span className="text-sm text-slate-700 leading-relaxed font-medium">{step.message}</span>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </Card>

          {/* Applied Rules / Rationale */}
          {rationale.length > 0 && (
            <Card className="p-0 overflow-hidden border-slate-200 shadow-sm rounded-xl">
              <button 
                onClick={() => setRationaleOpen(!rationaleOpen)}
                className="w-full px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between hover:bg-slate-100 transition-colors group cursor-pointer"
              >
                <div>
                  <h3 className="text-[13px] font-semibold text-slate-900 text-left flex items-center gap-2 uppercase tracking-wide">
                    Policy Rules Evaluated
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-1 font-medium">{rationale.length} policy conditions analyzed</p>
                </div>
                {rationaleOpen ? <ChevronUp size={16} className="text-slate-400 group-hover:text-slate-600" /> : <ChevronDown size={16} className="text-slate-400 group-hover:text-slate-600" />}
              </button>
              
              <AnimatePresence>
                {rationaleOpen && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="p-6 bg-slate-50/50 space-y-4">
                      {rationale.map((r: any, idx: number) => (
                        <div key={idx} className="p-5 rounded-xl border border-slate-200 bg-white shadow-sm space-y-4 hover:border-slate-300 transition-colors">
                          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
                            <span className="text-sm font-semibold text-slate-900">{r.rule_triggered}</span>
                            <span className="text-[10px] text-indigo-700 font-mono bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100 font-semibold">{r.policy_reference}</span>
                          </div>
                          <p className="text-sm text-slate-600 leading-relaxed font-medium">{r.human_explanation}</p>
                          
                          <div className="flex gap-8 pt-3 bg-slate-50 p-3 rounded-lg border border-slate-100">
                            <div className="flex flex-col gap-1">
                              <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Computed</span>
                              <span className="font-mono text-sm text-slate-900">{r.computed_value}</span>
                            </div>
                            <div className="flex flex-col gap-1">
                              <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Threshold</span>
                              <span className="font-mono text-sm text-slate-900">{r.threshold_value}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </Card>
          )}

          {/* Actionable Checklist (Manual Review) */}
          {handlerChecklist && handlerChecklist.items && handlerChecklist.items.length > 0 && (
            <Card className="p-0 overflow-hidden border-indigo-200 shadow-sm rounded-xl">
              <div className="px-6 py-4 border-b border-indigo-100 bg-indigo-50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ClipboardCheck size={16} className="text-indigo-700" />
                  <div className="text-left">
                    <h3 className="text-[13px] font-bold text-indigo-900 uppercase tracking-wide">Required Actions</h3>
                  </div>
                </div>
                <span className="text-[11px] font-bold text-indigo-700 bg-indigo-100/80 px-2.5 py-1 rounded-full uppercase tracking-wider">
                  Est. {handlerChecklist.total_estimated_minutes} min
                </span>
              </div>
              
              <div className="p-0 bg-white">
                {handlerChecklist.items.map((item: any, idx: number) => (
                  <div key={idx} className="flex gap-4 p-5 border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors group cursor-pointer">
                    <div className="mt-0.5">
                      <div className="w-5 h-5 rounded-md border-2 border-slate-300 bg-white group-hover:border-indigo-400 transition-colors" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-slate-900">{item.action}</p>
                      <p className="text-sm text-slate-500 mt-1.5 leading-relaxed">{item.reason}</p>
                      <div className="flex items-center gap-3 mt-3">
                        <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold bg-slate-100 px-2 py-0.5 rounded">{item.source_agent}</span>
                        <span className="text-[10px] text-slate-600 font-mono px-2 py-0.5 bg-slate-100 rounded border border-slate-200">{item.estimated_minutes}m</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                          item.priority === 'high' ? 'bg-red-50 text-red-700 border border-red-100' : 'bg-slate-100 text-slate-600 border border-slate-200'
                        }`}>{item.priority}</span>
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

