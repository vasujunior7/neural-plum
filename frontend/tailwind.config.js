/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'IBM Plex Sans', 'sans-serif'],
        mono: ['Geist Mono', 'JetBrains Mono', 'monospace'],
      },
      colors: {
        primary: {
          DEFAULT: '#0F172A', // slate-900
          light: '#334155', // slate-700
          dark: '#020617', // slate-950
          subtle: '#F1F5F9', // slate-100
        },
        secondary: {
          DEFAULT: '#3B82F6', // blue-500
          hover: '#2563EB', // blue-600
        },
        cta: {
          DEFAULT: '#0F172A', // slate-900
          hover: '#1E293B', // slate-800
        },
        background: {
          DEFAULT: '#F8FAFC', // slate-50
          panel: '#FFFFFF',
        },
        text: {
          primary: '#0F172A', // slate-900
          secondary: '#475569', // slate-600
          muted: '#94A3B8', // slate-400
        },
        border: {
          DEFAULT: '#E2E8F0', // slate-200
          subtle: '#F1F5F9', // slate-100
          strong: '#CBD5E1', // slate-300
        },
        status: {
          success: '#10B981', // emerald-500
          success_bg: '#D1FAE5', // emerald-100
          warning: '#F59E0B', // amber-500
          warning_bg: '#FEF3C7', // amber-100
          error: '#EF4444', // red-500
          error_bg: '#FEE2E2', // red-100
          info: '#3B82F6', // blue-500
          info_bg: '#DBEAFE', // blue-100
        },
      },
      borderRadius: {
        DEFAULT: '0.375rem', // 6px - sharp, industrial look
        md: '0.5rem', // 8px
        lg: '0.75rem', // 12px
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'panel': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.2s ease-out',
        'slide-down': 'slideDown 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(5px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-5px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
