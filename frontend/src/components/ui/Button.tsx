import { forwardRef } from "react"
import { motion } from "framer-motion"
import { cn } from "../../utils/cn"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "cta" | "outline" | "ghost"
  size?: "sm" | "md" | "lg"
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    return (
      <motion.button
        ref={ref}
        whileTap={{ scale: 0.98 }}
        className={cn(
          "inline-flex items-center justify-center rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-secondary disabled:pointer-events-none disabled:opacity-50 cursor-pointer shadow-sm border border-transparent",
          {
            "bg-primary text-white hover:bg-primary-light": variant === "primary",
            "bg-cta text-white hover:bg-cta-hover": variant === "cta",
            "bg-white border-border text-text-primary hover:bg-slate-50 hover:border-slate-300": variant === "outline",
            "bg-transparent shadow-none border-transparent hover:bg-slate-100 text-text-primary": variant === "ghost",
            "h-8 px-3 text-xs": size === "sm",
            "h-10 px-4 py-2 text-sm": size === "md",
            "h-12 px-8 text-base": size === "lg",
          },
          className
        )}
        {...(props as any)}
      />
    )
  }
)
Button.displayName = "Button"

