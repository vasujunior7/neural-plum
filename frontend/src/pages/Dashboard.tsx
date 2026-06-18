import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Card } from "../components/ui/Card"
import { Badge } from "../components/ui/Badge"
import { Button } from "../components/ui/Button"
import { fetchClaims } from "../utils/api"
import { TrendingUp, AlertCircle, Clock, ShieldCheck, RefreshCw, PlusCircle, ChevronRight } from "lucide-react"
import { useNavigate } from "react-router-dom"

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 }
}

export function Dashboard() {
  const [claims, setClaims] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const loadData = async () => {
    setLoading(true)
    try {
      const data = await fetchClaims()
      // Sort by newest first assuming the id format is monotonic or we just reverse
      setClaims(data.reverse())
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-8">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary tracking-tight">Command Center</h1>
          <p className="text-text-secondary mt-1 text-sm">Real-time claim adjudication matrix.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={loadData} variant="outline" className="gap-2" size="sm">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            Refresh
          </Button>
          <Button onClick={() => navigate('/submit')} variant="primary" className="gap-2" size="sm">
            <PlusCircle size={14} />
            New Claim
          </Button>
        </div>
      </header>

      {/* KPI Bento Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="flex flex-col gap-2 p-5">
          <span className="text-xs font-mono text-text-secondary uppercase tracking-wider flex items-center gap-2">
            <ActivityIcon /> Total Volume
          </span>
          <span className="text-3xl font-bold text-primary">{loading ? "-" : claims.length}</span>
        </Card>
        <Card className="flex flex-col gap-2 p-5">
          <span className="text-xs font-mono text-text-secondary uppercase tracking-wider flex items-center gap-2">
            <ShieldCheck size={14} className="text-status-success" /> Auto-Approved
          </span>
          <span className="text-3xl font-bold text-status-success">
            {loading ? "-" : claims.filter(c => c.decision === "APPROVED").length}
          </span>
        </Card>
        <Card className="flex flex-col gap-2 p-5">
          <span className="text-xs font-mono text-text-secondary uppercase tracking-wider flex items-center gap-2">
            <AlertCircle size={14} className="text-status-error" /> Rejected
          </span>
          <span className="text-3xl font-bold text-status-error">
            {loading ? "-" : claims.filter(c => c.decision === "REJECTED").length}
          </span>
        </Card>
        <Card className="flex flex-col gap-2 p-5">
          <span className="text-xs font-mono text-text-secondary uppercase tracking-wider flex items-center gap-2">
            <Clock size={14} className="text-status-warning" /> Manual Review
          </span>
          <span className="text-3xl font-bold text-status-warning">
            {loading ? "-" : claims.filter(c => c.decision === "MANUAL_REVIEW").length}
          </span>
        </Card>
      </div>

      {/* Claims Table */}
      <Card className="p-0 overflow-hidden">
        <div className="px-5 py-3 border-b border-border bg-slate-50 flex justify-between items-center">
          <h2 className="text-sm font-semibold text-primary">Recent Transactions</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white border-b border-border">
                <th className="px-5 py-3 text-xs font-mono text-text-muted uppercase tracking-widest">ID</th>
                <th className="px-5 py-3 text-xs font-mono text-text-muted uppercase tracking-widest">Patient</th>
                <th className="px-5 py-3 text-xs font-mono text-text-muted uppercase tracking-widest">Type</th>
                <th className="px-5 py-3 text-xs font-mono text-text-muted uppercase tracking-widest text-center">Status</th>
                <th className="px-5 py-3 text-xs font-mono text-text-muted uppercase tracking-widest text-right">Confidence</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            
            <motion.tbody 
              variants={containerVariants}
              initial="hidden"
              animate={loading ? "hidden" : "visible"}
              className="divide-y divide-border-subtle bg-white"
            >
              {claims.map((claim) => (
                <motion.tr 
                  key={claim.id} 
                  variants={itemVariants}
                  onClick={() => navigate(`/claims/${claim.id}`)}
                  className="hover:bg-slate-50 transition-colors cursor-pointer group"
                >
                  <td className="px-5 py-3 font-mono text-sm text-primary">#{claim.id}</td>
                  <td className="px-5 py-3 text-sm font-medium text-text-primary">{claim.member_id}</td>
                  <td className="px-5 py-3 text-sm text-text-secondary">{claim.claim_category}</td>
                  <td className="px-5 py-3 text-center">
                    <Badge variant={
                      claim.decision === 'APPROVED' ? 'success' : 
                      claim.decision === 'REJECTED' ? 'error' : 
                      claim.decision === 'MANUAL_REVIEW' ? 'warning' : 'default'
                    }>
                      {claim.decision ? claim.decision.replace('_', ' ') : claim.status}
                    </Badge>
                  </td>
                  <td className="px-5 py-3 font-mono text-sm text-right text-text-secondary">
                    {claim.confidence !== undefined && claim.confidence !== null ? `${(claim.confidence * 100).toFixed(1)}%` : '-'}
                  </td>
                  <td className="px-5 py-3 text-right">
                    <ChevronRight size={16} className="text-text-muted group-hover:text-primary transition-colors" />
                  </td>
                </motion.tr>
              ))}
              
              {!loading && claims.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-sm text-text-muted">
                    No claims found.
                  </td>
                </tr>
              )}
            </motion.tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

function ActivityIcon() {
  return <TrendingUp size={14} className="text-primary" />
}

