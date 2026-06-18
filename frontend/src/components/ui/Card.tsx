import { forwardRef } from "react"
import { motion } from "framer-motion"
import type { HTMLMotionProps } from "framer-motion"
import { cn } from "../../utils/cn"

export interface CardProps extends HTMLMotionProps<"div"> {
  interactive?: boolean
  panel?: boolean
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, interactive = false, panel = false, ...props }, ref) => {
    return (
      <motion.div
        ref={ref}
        className={cn(
          "bg-background-panel border border-border shadow-sm rounded-lg overflow-hidden",
          panel ? "bg-slate-50 border-slate-200" : "",
          interactive ? "cursor-pointer hover:border-border-strong hover:shadow transition-all duration-200" : "",
          className
        )}
        {...props}
      />
    )
  }
)
Card.displayName = "Card"
