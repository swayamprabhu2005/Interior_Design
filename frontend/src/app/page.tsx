'use client'



import Link from 'next/link'
import { useRouter } from 'next/navigation'

import { motion, AnimatePresence } from 'framer-motion'

import Navbar from '@/components/Navbar'

import FurnitureButton from '@/components/FurnitureButton'

import BeforeAfterSlider from '@/components/BeforeAfterSlider'

import { useAuthStore } from '@/stores/authStore'

import { useState, useEffect } from 'react'

import {

  Sparkles, Star, Zap, Shield, Clock, Users,

  ChevronLeft, ChevronRight, LayoutGrid, Palette,

  Image as ImageIcon, FileText, Play, Phone, CheckCircle2,

  Maximize2, Box, Eye

} from 'lucide-react'



const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'



const VIBE_SLIDES = [

  {

    id: 'modern',

    name: 'Modern Minimalist',

    tagline: 'Clean architectural lines, neutral tones, and intentional negative space',

    image: '/images/hero/living_room_hero.webp',

    fallback: `${BACKEND_URL}/static/assets/catalog/design_vibe/Modern.webp`,

    palettePreview: ['#161D1A', '#E2EDE7', '#A3E635'],

  },

  {

    id: 'scandinavian',

    name: 'Scandinavian Hygge',

    tagline: 'Light blonde oak, cozy boucle textures, and sunlit natural warmth',

    image: '/images/hero/bedroom_suite_hero.webp',

    fallback: `${BACKEND_URL}/static/assets/catalog/design_vibe/Scandinavian.webp`,

    palettePreview: ['#F4F6F4', '#E2B870', '#34D399'],

  },

  {

    id: 'japandi',

    name: 'Japandi Sanctuary',

    tagline: 'Wabi-sabi serenity, organic blonde wood, and artisan paper light',

    image: '/images/hero/japandi_hero.webp',

    fallback: `${BACKEND_URL}/static/assets/catalog/design_vibe/Japandi.webp`,

    palettePreview: ['#1B2420', '#C3DBCF', '#FDE047'],

  },

  {

    id: 'indo_minimalistic',

    name: 'Indo-Minimalistic',

    tagline: 'Handcrafted teakwood, artisanal cane weave, and warm terracotta tones',

    image: '/images/hero/indo_minimalistic_hero.webp',

    fallback: `${BACKEND_URL}/static/assets/catalog/design_vibe/Indo_Minimalistic.webp`,

    palettePreview: ['#B85D3B', '#F59E0B', '#161D1A'],

  },

]



const STEPS = [

  {

    icon: LayoutGrid,

    title: 'Choose Property & BHK',

    desc: 'Select your home structure and explore tailored architectural floor plans.',

    accent: 'bg-emerald-50 text-emerald-800 border-emerald-200/60',

  },

  {

    icon: Palette,

    title: 'Select Materials & Fabrics',

    desc: 'Pick laminate finishes and fabric textures with real-time price tracking.',

    accent: 'bg-amber-50 text-amber-800 border-amber-200/60',

  },

  {

    icon: Zap,

    title: 'Customise Room-by-Room',

    desc: 'Swap items, change attributes, and track budget variations in real time.',

    accent: 'bg-lime-50 text-lime-800 border-lime-200/60',

  },

  {

    icon: ImageIcon,

    title: '4-Wall AI Renders',

    desc: 'Visualize your curated rooms in photorealistic multi-angle perspectives.',

    accent: 'bg-teal-50 text-teal-800 border-teal-200/60',

  },

  {

    icon: FileText,

    title: 'Quote & Execution',

    desc: 'Download bank-compliant PDF quotes and begin execution with verified teams.',

    accent: 'bg-emerald-50 text-emerald-800 border-emerald-200/60',

  },

]



const TESTIMONIALS = [

  {

    name: 'Priya Mehta',

    city: 'Bangalore • 3BHK Penthouse',

    rating: 5,

    text: 'Got my entire 3BHK designed in one afternoon! The AI renders looked exactly like the final installed wood joinery and lighting result.',

    avatar: 'PM',

  },

  {

    name: 'Rahul Sharma',

    city: 'Mumbai • 2BHK Sea-Facing',

    rating: 5,

    text: 'The quotation PDF was so clean and bank-compliant that my mortgage loan approval cleared in 48 hours without item disputes.',

    avatar: 'RS',

  },

  {

    name: 'Ananya Iyer',

    city: 'Goa • 4BHK Villa',

    rating: 5,

    text: 'Loved the Scandinavian package. The 3D room viewer and real-time inventory locking made the whole execution stress-free.',

    avatar: 'AI',

  },

]



export default function LandingPage() {

  const { isLoggedIn } = useAuthStore()

  const router = useRouter()
  const handleNavigateCTA = (e?: React.MouseEvent) => {
    if (e) e.preventDefault()
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (token || isLoggedIn) {
      router.push('/dashboard')
    } else {
      router.push('/login')
    }
  }

  const [currentSlide, setCurrentSlide] = useState(0)

  const [isHovered, setIsHovered] = useState(false)



  // Auto-slide carousel every 6s with pause on hover

  useEffect(() => {

    if (isHovered) return

    const timer = setInterval(() => {

      setCurrentSlide((prev) => (prev + 1) % VIBE_SLIDES.length)

    }, 6000)

    return () => clearInterval(timer)

  }, [isHovered])



  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % VIBE_SLIDES.length)

  const prevSlide = () => setCurrentSlide((prev) => (prev === 0 ? VIBE_SLIDES.length - 1 : prev - 1))



  return (

    <div className="min-h-screen bg-[#FAFBF9] text-[#161D1A]">

      <Navbar />



      {/* ── Main Container: Airy Light Canvas with Hero Showcase Frame ───────── */}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-20 space-y-24">



        {/* ── HERO SHOWCASE CHASSIS (Directly inspired by Image 1) ───────────── */}

        <section

          className="relative w-full rounded-[2.25rem] sm:rounded-[2.75rem] overflow-hidden border border-emerald-950/15 shadow-[0_20px_50px_rgba(22,29,26,0.12)] bg-[#0B0F0D] text-white min-h-[640px] sm:min-h-[720px] lg:min-h-[760px] flex flex-col justify-between p-6 sm:p-10 lg:p-14"

          onMouseEnter={() => setIsHovered(true)}

          onMouseLeave={() => setIsHovered(false)}

        >

          {/* Background Cross-Fade Image Carousel */}

          <AnimatePresence mode="sync">

            <motion.div

              key={VIBE_SLIDES[currentSlide].id}

              initial={{ opacity: 0, scale: 1.05 }}

              animate={{ opacity: 1, scale: 1 }}

              exit={{ opacity: 0 }}

              transition={{ duration: 1.1, ease: 'easeOut' }}

              className="absolute inset-0 z-0"

            >

              <img

                src={VIBE_SLIDES[currentSlide].image}

                alt={VIBE_SLIDES[currentSlide].name}

                onError={(e) => {

                  const target = e.currentTarget as HTMLImageElement

                  if (!target.dataset.fallbackTried) {

                    target.dataset.fallbackTried = 'true'

                    target.src = VIBE_SLIDES[currentSlide].fallback

                  }

                }}

                className="w-full h-full object-cover object-center"

              />

            </motion.div>

          </AnimatePresence>



          {/* Cinematic Vignette Overlay for Crisp Readability */}

          <div className="absolute inset-0 z-1 bg-gradient-to-t from-black/85 via-black/40 to-black/60 pointer-events-none" />



          {/* Subtle Luminous Perimeter Rim Light */}

          <div className="absolute inset-0 z-1 pointer-events-none rounded-[2.25rem] sm:rounded-[2.75rem] border border-[#A3E635]/20 shadow-[inset_0_0_40px_rgba(163,230,53,0.12)]" />



          {/* ── Top Bar inside Showcase Frame (Image 1 header cues) ─────────── */}

          <div className="relative z-10 flex flex-wrap items-center justify-between gap-4">

            <div className="flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-black/45 backdrop-blur-md border border-white/20 text-xs font-semibold tracking-wide shadow-sm">

              <span className="w-2 h-2 rounded-full bg-[#A3E635] animate-ping" />

              <span className="text-[#A3E635] font-bold">INTERIORAI STUDIO</span>

              <span className="text-white/60">•</span>

              <span className="text-white/80">Architecture & Modular Execution</span>

            </div>



            

          </div>



          {/* ── Center Content: Big Headline & Action ──────────────────────── */}

          <div className="relative z-10 max-w-3xl my-auto py-8 space-y-6">

            {/* Active Vibe Chip */}

            <motion.div

              key={`badge-${currentSlide}`}

              initial={{ opacity: 0, y: -10 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.4 }}

              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/15 backdrop-blur-md border border-white/25 text-white text-xs font-bold tracking-wider uppercase shadow-md"

            >

              <Sparkles className="w-3.5 h-3.5 text-[#FDE047]" />

              <span>Design Vibe: {VIBE_SLIDES[currentSlide].name}</span>

            </motion.div>



            {/* Main Headline */}

            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-[1.10] drop-shadow-lg">

              Where Dream Homes{' '}

              <span className="bg-gradient-to-r from-[#FFFFFF] via-[#E2EDE7] to-[#A3E635] bg-clip-text text-transparent">

                Become Reality

              </span>

            </h1>



            {/* Subtitle */}

            <p className="text-base sm:text-lg text-white/90 max-w-xl font-normal leading-relaxed drop-shadow-md">

              Step into the future of interior architecture with interactive 3D spatial curation, dynamic price tracking, and turnkey master artisan execution.

            </p>



            {/* Action Buttons with FurnitureButton Morph */}

            <div className="flex flex-wrap items-center gap-4 pt-2">

              <FurnitureButton

                onClick={handleNavigateCTA}

                id="hero-cta"

                size="lg"

                variant="primary"

                icon="arrow"

              >

                Design My Home Free

              </FurnitureButton>



              <FurnitureButton

                href="#how-it-works"

                size="lg"

                variant="outline"

                icon="none"

              >

                Explore How It Works

              </FurnitureButton>

            </div>

          </div>



          {/* ── Bottom Section: Floating Capsules (Directly matching Image 1) ── */}

          <div className="relative z-10 grid grid-cols-1 md:grid-cols-12 gap-4 items-end pt-6 border-t border-white/15">



            {/* Floating Left Video Tour Capsule */}

            <div className="md:col-span-5 flex items-center gap-3.5 p-3 rounded-2xl bg-black/55 backdrop-blur-xl border border-white/20 shadow-xl">

              <div className="w-10 h-10 rounded-xl bg-[#161D1A] border border-white/15 flex items-center justify-center shrink-0 text-[#A3E635] shadow-inner">

                <Play className="w-4 h-4 fill-current ml-0.5" />

              </div>

              <div className="text-xs text-white/90 leading-snug">

                <p className="font-bold text-white">Explore 3D Spatial Curation</p>

                <p className="text-white/70 text-[11px] truncate">Interactive walkthroughs & real-time material switches</p>

              </div>

            </div>



            {/* Center: Sleek Slide Progress Ticker Indicator */}

            <div className="md:col-span-4 flex items-center justify-center gap-2 py-2">

              {VIBE_SLIDES.map((slide, idx) => (

                <button

                  key={slide.id}

                  type="button"

                  onClick={() => setCurrentSlide(idx)}

                  aria-label={`Go to ${slide.name}`}

                  className={`h-1.5 rounded-full transition-all duration-300 cursor-pointer ${

                    currentSlide === idx

                      ? 'w-8 bg-[#A3E635] shadow-[0_0_12px_rgba(163,230,53,0.5)]'

                      : 'w-2.5 bg-white/35 hover:bg-white/60'

                  }`}

                  title={slide.name}

                />

              ))}

            </div>



            {/* Floating Right Review Capsule & Floating Phone Action Button */}

            <div className="md:col-span-3 flex items-center justify-end gap-3">

              <div className="px-3.5 py-2 rounded-2xl bg-black/55 backdrop-blur-xl border border-white/20 text-right shadow-xl">

                <div className="flex items-center justify-end gap-1 text-[#FDE047] text-xs font-bold">

                  <span>★ 5.0 Google Rating</span>

                </div>

                <div className="text-[11px] text-white/75 font-medium">Mr. Savio Coutinho • Goa</div>

              </div>



              {/* Luminous Circular Call Action Button (Image 1 style) */}

              <Link

                href="/support"

                aria-label="Direct enquiry"

                className="w-12 h-12 rounded-full bg-[#A3E635] hover:bg-[#B5F442] text-[#0B0F0D] flex items-center justify-center shadow-[0_4px_20px_rgba(163,230,53,0.5)] transition-transform hover:scale-105 active:scale-95 shrink-0"

              >

                <Phone className="w-5 h-5 fill-current" />

              </Link>

            </div>

          </div>



          {/* Left/Right Carousel Nav Arrows */}

          <button

            type="button"

            onClick={prevSlide}

            aria-label="Previous slide"

            className="absolute left-3 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-black/40 hover:bg-black/70 text-white/80 hover:text-white backdrop-blur-md border border-white/20 flex items-center justify-center transition-all shadow-md active:scale-95"

          >

            <ChevronLeft className="w-5 h-5" />

          </button>

          <button

            type="button"

            onClick={nextSlide}

            aria-label="Next slide"

            className="absolute right-3 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-black/40 hover:bg-black/70 text-white/80 hover:text-white backdrop-blur-md border border-white/20 flex items-center justify-center transition-all shadow-md active:scale-95"

          >

            <ChevronRight className="w-5 h-5" />

          </button>

        </section>



        {/* ── BENTO GRID: Architectural Elegance Meets Spatial AI ────────────── */}

        <section className="space-y-10">

          <div className="text-center max-w-2xl mx-auto space-y-3">

            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-bold tracking-wider uppercase">

              <Sparkles className="w-3.5 h-3.5 text-[#10B981]" />

              <span>THE ARCHITECTURAL ADVANTAGE</span>

            </div>

            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#161D1A] tracking-tight">

              Designed with Precision. Built with Master Artisans.

            </h2>

            <p className="text-stone-600 text-sm sm:text-base leading-relaxed">

              Every detail is engineered to deliver showroom-level interiors with zero hidden markups or guesswork.

            </p>

          </div>



          {/* 4-Card Bento Grid */}

          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">



            {/* Card 1 (Span 7 Col): Interactive 3D Spatial Canvas */}

            <div className="md:col-span-7 bg-white rounded-3xl p-8 border border-stone-200/90 shadow-[0_4px_24px_rgba(0,0,0,0.03)] hover:shadow-xl transition-all card-hover flex flex-col justify-between">

              <div className="space-y-3">

                <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center">

                  <Box className="w-6 h-6 text-[#10B981]" />

                </div>

                <h3 className="text-2xl font-bold text-[#161D1A]">Interactive 3D Spatial Canvas</h3>

                <p className="text-stone-600 text-sm leading-relaxed max-w-lg">

                  Powered by WebGL and Three.js. Orbit, zoom, inspect clearance envelopes, and test laminate finishes directly in the browser before breaking ground.

                </p>

              </div>



              {/* Visual Mockup inside Bento Card */}

              <div className="mt-6 pt-6 border-t border-stone-100 flex items-center justify-between text-xs text-stone-500 font-semibold">

                <span className="flex items-center gap-1.5 text-emerald-700">

                  <CheckCircle2 className="w-4 h-4 text-[#10B981]" />

                  Automatic Pillar Clearance

                </span>

                <span className="flex items-center gap-1.5 text-emerald-700">

                  <CheckCircle2 className="w-4 h-4 text-[#10B981]" />

                  Zero-Balcony Compliance

                </span>

              </div>

            </div>



            {/* Card 2 (Span 5 Col): 15-Second AI Render Engine */}

            <div className="md:col-span-5 bg-white rounded-3xl p-8 border border-stone-200/90 shadow-[0_4px_24px_rgba(0,0,0,0.03)] hover:shadow-xl transition-all card-hover flex flex-col justify-between">

              <div className="space-y-3">

                <div className="w-12 h-12 rounded-2xl bg-lime-50 text-lime-700 flex items-center justify-center">

                  <Sparkles className="w-6 h-6 text-[#84CC16]" />

                </div>

                <h3 className="text-2xl font-bold text-[#161D1A]">15-Second AI Renders</h3>

                <p className="text-stone-600 text-sm leading-relaxed">

                  Generate 4-Wall photorealistic perspectives using Gemini Vision and Imagen 3. See exactly how natural daylight enters your room.

                </p>

              </div>



              <div className="mt-6 pt-4 border-t border-stone-100 flex items-center gap-2">

                <span className="px-3 py-1 rounded-full bg-[#FAFBF9] border border-stone-200 text-xs font-bold text-stone-700">

                  Wall A • B • C • D Views

                </span>

              </div>

            </div>



            {/* Card 3 (Span 5 Col): Real-Time Transparent Pricing */}

            <div className="md:col-span-5 bg-white rounded-3xl p-8 border border-stone-200/90 shadow-[0_4px_24px_rgba(0,0,0,0.03)] hover:shadow-xl transition-all card-hover flex flex-col justify-between">

              <div className="space-y-3">

                <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center">

                  <Zap className="w-6 h-6 text-[#F59E0B]" />

                </div>

                <h3 className="text-2xl font-bold text-[#161D1A]">Real-Time Pricing Ledger</h3>

                <p className="text-stone-600 text-sm leading-relaxed">

                  Every customization instantly updates your line-item quotation. No hidden charges, no surprises at checkout.

                </p>

              </div>



              <div className="mt-6 pt-4 border-t border-stone-100 flex items-center gap-3 text-xs font-bold text-stone-700">

                <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">

                  Bank-Compliant PDF Quotes

                </span>

              </div>

            </div>



            {/* Card 4 (Span 7 Col): Verified Master Artisans & Execution */}

            <div className="md:col-span-7 bg-white rounded-3xl p-8 border border-stone-200/90 shadow-[0_4px_24px_rgba(0,0,0,0.03)] hover:shadow-xl transition-all card-hover flex flex-col justify-between">

              <div className="space-y-3">

                <div className="w-12 h-12 rounded-2xl bg-teal-50 text-teal-700 flex items-center justify-center">

                  <Shield className="w-6 h-6 text-[#059669]" />

                </div>

                <h3 className="text-2xl font-bold text-[#161D1A]">Master Artisans & KYC Verification</h3>

                <p className="text-stone-600 text-sm leading-relaxed max-w-lg">

                  Every contractor and carpenter is vetted, geo-assigned, and tracked on-site through daily progress checklists and multi-angle photo proof uploads.

                </p>

              </div>



              <div className="mt-6 pt-6 border-t border-stone-100 flex items-center justify-between text-xs text-stone-600 font-bold">

                <span>Dual-Track Progression (Sourcing + Site Installation)</span>

                <span className="text-[#84CC16]">Strict Zero-Date Policy ✓</span>

              </div>

            </div>



          </div>

        </section>



        {/* ── BEFORE & AFTER INTERACTIVE TRANSFORMATION SLIDER ─────────────────── */}

        <BeforeAfterSlider />



        {/* ── 5-STEP JOURNEY: From Idea to Turnkey Reality ─────────────────────── */}

        <section id="how-it-works" className="space-y-12">

          <div className="text-center max-w-2xl mx-auto space-y-3">

            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#161D1A] tracking-tight">

              From Idea to Reality in 5 Steps

            </h2>

            <p className="text-stone-600 text-sm sm:text-base leading-relaxed">

              Our guided design wizard walks you through everything — zero interior design experience needed.

            </p>

          </div>



          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">

            {STEPS.map((step, i) => (

              <motion.div

                key={step.title}

                initial={{ opacity: 0, y: 20 }}

                whileInView={{ opacity: 1, y: 0 }}

                viewport={{ once: true }}

                transition={{ delay: i * 0.08 }}

                className="bg-white p-6 rounded-3xl border border-stone-200/80 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center text-center space-y-4"

              >

                <div className={`w-14 h-14 rounded-2xl ${step.accent} flex items-center justify-center shadow-xs border`}>

                  <step.icon className="w-6 h-6" />

                </div>

                <div className="text-[11px] font-extrabold text-[#84CC16] tracking-wider uppercase">

                  STEP 0{i + 1}

                </div>

                <h3 className="font-bold text-[#161D1A] text-sm">{step.title}</h3>

                <p className="text-xs text-stone-500 leading-relaxed font-medium">{step.desc}</p>

              </motion.div>

            ))}

          </div>

        </section>



        {/* ── TESTIMONIALS: Loved by Discerning Homeowners ────────────────────── */}

        <section className="space-y-12 bg-white rounded-3xl p-8 sm:p-12 border border-stone-200/80 shadow-sm">

          <div className="text-center max-w-xl mx-auto space-y-2">

            <div className="flex items-center justify-center gap-1">

              {[1, 2, 3, 4, 5].map((s) => (

                <Star key={s} className="w-4 h-4 fill-[#FDE047] text-[#FDE047]" />

              ))}

            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#161D1A]">

              Loved by Homeowners Across India

            </h2>

            <p className="text-stone-500 text-xs sm:text-sm">Real projects delivered across Goa, Bangalore, and Mumbai.</p>

          </div>



          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {TESTIMONIALS.map((t, idx) => (

              <div

                key={idx}

                className="p-6 rounded-2xl bg-[#FAFBF9] border border-stone-200/70 space-y-4 flex flex-col justify-between"

              >

                <div className="space-y-3">

                  <div className="flex items-center gap-1">

                    {Array.from({ length: t.rating }).map((_, j) => (

                      <Star key={j} className="w-3.5 h-3.5 fill-[#FDE047] text-[#FDE047]" />

                    ))}

                  </div>

                  <p className="text-xs sm:text-sm text-stone-700 leading-relaxed italic font-medium">

                    &quot;{t.text}&quot;

                  </p>

                </div>



                <div className="flex items-center gap-3 pt-3 border-t border-stone-200/60">

                  <div className="w-9 h-9 rounded-full bg-[#161D1A] text-[#A3E635] font-extrabold text-xs flex items-center justify-center">

                    {t.avatar}

                  </div>

                  <div>

                    <div className="text-xs font-bold text-[#161D1A]">{t.name}</div>

                    <div className="text-[11px] text-stone-500">{t.city}</div>

                  </div>

                </div>

              </div>

            ))}

          </div>

        </section>



        {/* ── CALL TO ACTION BANNER ───────────────────────────────────────────── */}

        <section className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-[#161D1A] to-[#1F2B26] text-white p-10 sm:p-14 text-center space-y-6 shadow-xl">

          <div className="max-w-2xl mx-auto space-y-3">

            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">

              Ready to Design Your Dream Home?

            </h2>

            <p className="text-white/80 text-sm sm:text-base leading-relaxed">

              Start with our free 6-step architectural onboarding wizard. Explore instant pricing, 3D layouts, and curated design vibes.

            </p>

          </div>



          <div className="flex justify-center pt-2">

            <FurnitureButton

              onClick={handleNavigateCTA}

              size="lg"

              variant="primary"

              icon="arrow"

            >

              Start Free Design Journey

            </FurnitureButton>

          </div>

        </section>



      </main>



      {/* ── ARCHITECTURAL FOOTER ──────────────────────────────────────────────── */}

      <footer className="bg-[#161D1A] text-stone-400 py-12 border-t border-stone-800 text-xs sm:text-sm">

        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">

          <div className="flex items-center gap-2">

            <Sparkles className="w-4 h-4 text-[#A3E635]" />

            <span className="font-extrabold text-white text-base tracking-wide">

              Interior<span className="text-[#A3E635]">AI</span>

            </span>

          </div>



          <p className="text-stone-400 text-center sm:text-left">

            © 2026 InteriorAI Platform. End-to-end AI interior design & modular execution.

          </p>



          <div className="flex items-center gap-4 text-xs font-semibold text-stone-300">

            <Link href="/" className="hover:text-white transition">Home</Link>

            <Link href="/support" className="hover:text-white transition">Support</Link>

            <Link href="/login" className="hover:text-white transition">Sign In</Link>

          </div>

        </div>

      </footer>

    </div>

  )

}

