import { forwardRef } from "react"
import { cn } from "../../utils/cn"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "warning" | "error" | "info"
}

export const Badge = forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold font-mono tracking-widest uppercase transition-colors focus:outline-none focus:ring-2 focus:ring-secondary focus:ring-offset-2",
          {
            "bg-slate-100 text-slate-600 border-slate-200": variant === "default",
            "bg-status-success_bg text-status-success border-status-success/20": variant === "success",
            "bg-status-warning_bg text-status-warning border-status-warning/20": variant === "warning",
            "bg-status-error_bg text-status-error border-status-error/20": variant === "error",
            "bg-status-info_bg text-status-info border-status-info/20": variant === "info",
          },
          className
        )}
        {...props}
      />
    )
  }
)
Badge.displayName = "Badge"

