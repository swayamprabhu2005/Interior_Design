import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        pine: {
          50:  '#f2f6f4',
          100: '#e2ede7',
          200: '#c3dbcf',
          300: '#96c2af',
          400: '#62a289',
          500: '#3d856d',
          600: '#2c6a56',
          700: '#245445',
          800: '#1f4338',
          900: '#161D1A', // Frosted Pine Tint
          950: '#0B0F0D', // Deep Obsidian Pine
        },
        lime: {
          50:  '#f7fee7',
          100: '#ecfccb',
          200: '#d9f99d',
          300: '#bef264',
          400: '#A3E635', // Luminous Lime Accent
          500: '#84CC16', // Deep Lime Accent
          600: '#65a30d',
          700: '#4d7c0f',
          800: '#3f6212',
          900: '#365314',
        },
        emerald: {
          50:  '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34D399', // Emerald Sage
          500: '#10B981', // Vibrant Mint Emerald
          600: '#059669', // Deep Forest
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        champagne: {
          50:  '#fbf9f3',
          100: '#f6f1e3',
          200: '#ebe1c4',
          300: '#F5D699',
          400: '#E2B870', // Brushed Champagne Gold
          500: '#c5a059',
          600: '#a37736',
          700: '#835a2c',
        },
        solarium: {
          300: '#FEF08A',
          400: '#FDE047', // Warm Solarium Yellow
          500: '#F59E0B', // Warm Lumina Amber
          600: '#D97706',
        },
        alabaster: {
          50:  '#FAFBF9', // Ultra-Light Luxury Canvas
          100: '#F4F6F4', // Architectural Mist
          200: '#EAEFEA',
          300: '#DDE5DD',
          400: '#C7D4C7',
          500: '#A3B4A3',
        },
        indigo: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        amber: {
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
        },
        terracotta: {
          50:  '#fdf6f2',
          100: '#faeae3',
          200: '#f5d6c8',
          300: '#ebb6a0',
          400: '#dc8d6f',
          500: '#cc6d49',
          600: '#b85d3b',
          700: '#9b4a2e',
          800: '#7f3e29',
          900: '#683626',
          950: '#381911',
        },
        atelier: {
          50:  '#faf8f5',
          100: '#f5f2eb',
          200: '#eae4d8',
          300: '#dbcfbc',
          400: '#c4b299',
          500: '#ab9579',
          600: '#937c62',
          700: '#77634f',
          800: '#615142',
          900: '#292524',
          950: '#181614',
        },
        greige: {
          50:  '#faf8f5',
          100: '#f5f2ec',
          200: '#ece7dd',
          300: '#ded7ca',
          400: '#c5bcad',
          500: '#a89c8b',
          600: '#8d806e',
        },
        sage: {
          50:  '#f4f6f4',
          100: '#e5eae4',
          500: '#4e5b4b',
          600: '#404c3d',
          700: '#343e32',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'hero-gradient': 'linear-gradient(145deg, #0B0F0D 0%, #161D1A 45%, #1B2923 75%, #0B0F0D 100%)',
        'light-luxury': 'radial-gradient(ellipse at top, #FFFFFF 0%, #FAFBF9 50%, #F4F6F4 100%)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'cushion-bounce': 'cushionBounce 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':       { transform: 'translateY(-12px)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        cushionBounce: {
          '0%': { transform: 'scale(1)' },
          '40%': { transform: 'scaleY(0.90) scaleX(1.05)' },
          '75%': { transform: 'scaleY(1.04) scaleX(0.98)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      boxShadow: {
        'glow-lime': '0 0 30px rgba(163, 230, 53, 0.35)',
        'glow-emerald': '0 0 30px rgba(16, 185, 129, 0.3)',
        'glow-champagne': '0 0 30px rgba(226, 184, 112, 0.35)',
        'lounge': '0 12px 36px -4px rgba(22, 29, 26, 0.08), 0 4px 14px -2px rgba(22, 29, 26, 0.04)',
        'card': '0 8px 32px rgba(22, 29, 26, 0.05)',
        'card-hover': '0 20px 48px -8px rgba(22, 29, 26, 0.10)',
      },
    },
  },
  plugins: [],
}
export default config
