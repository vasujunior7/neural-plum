import { LayoutDashboard, FileText, Activity } from "lucide-react"
import { Link, useLocation } from "react-router-dom"
import { cn } from "../../utils/cn"

export function Sidebar() {
  const location = useLocation()
  
  return (
    <aside className="bg-background-panel border-r border-border w-64 h-screen fixed left-0 top-0 flex flex-col pt-6 z-20">
      <div className="px-6 mb-10 flex items-center gap-3">
        <div className="relative flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-slate-900 to-slate-800 shadow-md border border-slate-700/50 overflow-hidden">
          {/* Subtle inner glow */}
          <div className="absolute inset-0 bg-gradient-to-b from-white/10 to-transparent"></div>
          
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="relative z-10 drop-shadow-sm">
            {/* Main plum body */}
            <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="url(#plum_grad)" />
            {/* Inner highlight */}
            <path d="M12 22C15.3137 22 18 19.3137 18 16C18 12.6863 15.3137 10 12 10C8.68629 10 6 12.6863 6 16C6 19.3137 8.68629 22 12 22Z" fill="white" fillOpacity="0.95" />
            {/* Plum leaves */}
            <path d="M12 10C12 10 14.5 4.5 18.5 3C15.5 2.5 12.5 5.5 12 8C11.5 5.5 8.5 2.5 5.5 3C9.5 4.5 12 10 12 10Z" fill="#10B981" />
            <defs>
              <linearGradient id="plum_grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                <stop stopColor="#A855F7" />
                <stop offset="1" stopColor="#4F46E5" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div className="flex flex-col">
          <span className="font-sans font-extrabold text-xl tracking-tight text-primary leading-none">Neural Plum</span>
          <span className="font-sans font-medium text-xs text-text-muted mt-1 uppercase tracking-wider">Claims</span>
        </div>
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
              await fetch('https://vasiuuu-neural-plum-app.hf.space/v1/claims', {
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

