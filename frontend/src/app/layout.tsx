import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from 'react-hot-toast'

export const metadata: Metadata = {
  title: 'InteriorAI — Designed & Delivered in a Week',
  description: 'Get your home interiors designed and executed in a week. Select packages starting from ₹3L, customize details in real-time, and get instant quotes.',
  keywords: 'interior design, modular furniture, home decor, 3D rendering, site delivery, quotation',
  openGraph: {
    title: 'InteriorAI — Designed & Delivered in a Week',
    description: 'Guaranteed design and execution in a week starting from ₹3L.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster
          position="top-right"
          containerStyle={{ top: '80px', right: '24px' }}
          toastOptions={{
            duration: 3500,
            icon: null, // Strictly text-only (zero ticks or checkmarks)
            style: {
              background: 'rgba(255, 255, 255, 0.96)',
              color: '#132A1C',
              backdropFilter: 'blur(16px)',
              borderRadius: '16px',
              border: '1px solid rgba(132, 204, 22, 0.45)',
              boxShadow: '0 14px 34px -4px rgba(22, 43, 30, 0.12), 0 4px 12px rgba(0, 0, 0, 0.04)',
              fontSize: '13.5px',
              fontWeight: '700',
              letterSpacing: '0.01em',
              padding: '12px 20px',
            },
            success: {
              icon: null,
              style: {
                background: 'rgba(255, 255, 255, 0.97)',
                color: '#132A1C',
                border: '1px solid rgba(132, 204, 22, 0.55)',
                borderLeft: '4px solid #84CC16',
              },
            },
            error: {
              icon: null,
              style: {
                background: 'rgba(255, 255, 255, 0.97)',
                color: '#991B1B',
                border: '1px solid rgba(239, 68, 68, 0.35)',
                borderLeft: '4px solid #EF4444',
              },
            },
          }}
        />
      </body>
    </html>
  )
}
