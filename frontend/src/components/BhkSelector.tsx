'use client'
import { motion } from 'framer-motion'
import { CheckCircle2 } from 'lucide-react'
import clsx from 'clsx'

const BHK_OPTIONS = [
  {
    id: '1BHK',
    label: '1 BHK',
    desc: 'Studio & compact modular living',
    priceFrom: '2.9L',
    image: '/images/bhk/1bhk.webp',
  },
  {
    id: '2BHK',
    label: '2 BHK',
    desc: 'Perfect for couples & modern families',
    priceFrom: '4.8L',
    image: '/images/bhk/2bhk.webp',
  },
  {
    id: '3BHK',
    label: '3 BHK',
    desc: 'Spacious multi-room family home',
    priceFrom: '6.8L',
    image: '/images/bhk/3bhk.webp',
  },
  {
    id: '4BHK',
    label: '4 BHK',
    desc: 'Expansive grand luxury residence',
    priceFrom: '9.5L',
    image: '/images/bhk/4bhk.webp',
  },
]

interface Props {
  selected?: string
  onSelect: (bhk: string) => void
}

export default function BhkSelector({ selected, onSelect }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 sm:gap-5">
      {BHK_OPTIONS.map((opt, i) => {
        const isSelected = selected === opt.id
        return (
          <motion.button
            key={opt.id}
            type="button"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, duration: 0.3 }}
            onClick={() => onSelect(opt.id)}
            className={clsx(
              'relative rounded-2xl border-2 text-left transition-all duration-300 group overflow-hidden flex flex-col justify-between cursor-pointer',
              isSelected
                ? 'border-[#84CC16] bg-[#FAFBF9] shadow-[0_10px_28px_-4px_rgba(132,204,22,0.25)] ring-2 ring-lime-400/25 scale-[1.01]'
                : 'border-stone-200/90 bg-white hover:border-[#84CC16]/60 hover:shadow-lg hover:-translate-y-0.5'
            )}
          >
            {/* Top 3D Isometric Cutaway Thumbnail */}
            <div className="relative w-full h-32 sm:h-36 overflow-hidden bg-stone-100">
              <img
                src={opt.image}
                alt={`${opt.label} architectural 3D cutaway`}
                className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500 ease-out"
                onError={(e) => {
                  // Fallback to stylized container if image load fails
                  const target = e.currentTarget as HTMLImageElement
                  target.style.display = 'none'
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent pointer-events-none" />

              {/* Selection Checkmark Badge */}
              {isSelected && (
                <div className="absolute top-2.5 right-2.5 bg-[#161D1A]/90 backdrop-blur-md text-[#A3E635] p-1 rounded-full shadow-md border border-[#A3E635]/40 flex items-center justify-center">
                  <CheckCircle2 className="w-4 h-4 fill-[#A3E635]/20" />
                </div>
              )}
            </div>

            {/* Content Details */}
            <div className="p-4 sm:p-5 flex-1 flex flex-col justify-between">
              <div>
                <div
                  className={clsx(
                    'text-lg sm:text-xl font-black tracking-tight mb-1 transition-colors',
                    isSelected ? 'text-[#0B0F0D]' : 'text-stone-900 group-hover:text-[#059669]'
                  )}
                >
                  {opt.label}
                </div>
                <div className="text-xs text-stone-500 leading-relaxed mb-4 min-h-[32px]">
                  {opt.desc}
                </div>
              </div>

              {/* Price Pill Footer (Zero Room Count) */}
              <div className="pt-3 border-t border-stone-100 flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider text-stone-400">
                  Starts At
                </span>
                <span
                  className={clsx(
                    'text-xs sm:text-sm font-black px-2.5 py-1 rounded-full transition-colors',
                    isSelected
                      ? 'bg-emerald-100 text-[#059669] border border-emerald-300/80 font-extrabold'
                      : 'bg-[#F4F6F4] text-stone-700 border border-stone-200'
                  )}
                >
                  from ₹{opt.priceFrom}
                </span>
              </div>
            </div>
          </motion.button>
        )
      })}
    </div>
  )
}
