import { LayoutDashboard, FileText, Users, Activity } from "lucide-react"
import { Link, useLocation } from "react-router-dom"
import { cn } from "../../utils/cn"

export function Sidebar() {
  const location = useLocation()
  
  return (
    <aside className="bg-background-panel border-r border-border w-64 h-screen fixed left-0 top-0 flex flex-col pt-6 z-20">
      <div className="px-6 mb-10 flex items-center gap-3">
        <div className="w-8 h-8 rounded-md bg-primary text-white flex items-center justify-center shadow-sm">
          <Activity size={18} />
        </div>
        <span className="font-sans font-bold text-lg text-primary">Plum Claims</span>
      </div>
      
      <nav className="flex-1 px-4 space-y-1">
        <Link 
          to="/" 
          className={cn(
            "flex items-center gap-3 px-3 py-2 rounded-md font-medium transition-colors text-sm",
            location.pathname === "/" 
              ? "bg-slate-100 text-primary" 
              : "text-text-secondary hover:text-primary hover:bg-slate-50"
          )}
        >
          <LayoutDashboard size={18} />
          Command Center
        </Link>
        <Link 
          to="/submit" 
          className={cn(
            "flex items-center gap-3 px-3 py-2 rounded-md font-medium transition-colors text-sm",
            location.pathname === "/submit" 
              ? "bg-slate-100 text-primary" 
              : "text-text-secondary hover:text-primary hover:bg-slate-50"
          )}
        >
          <FileText size={18} />
          Submit Claim
        </Link>
        <button 
          onClick={async () => {
            if(window.confirm('Are you sure you want to delete all claims?')) {
              await fetch('http://localhost:8000/v1/claims', {
                method: 'DELETE',
                headers: { 'X-API-Key': 'super-secret-plum-key' }
              });
              window.location.href = '/';
            }
          }}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-md font-medium transition-colors text-text-secondary hover:text-red-500 hover:bg-red-50 mt-8 text-sm"
        >
          <Activity size={18} />
          Reset All Claims
        </button>
      </nav>

      <div className="p-4 border-t border-border mt-auto">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-sm font-bold text-primary">
            AD
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-text-primary">Adjudicator</span>
            <span className="text-xs text-text-muted">ID: 884-21A</span>
          </div>
        </div>
      </div>
    </aside>
  )
}

