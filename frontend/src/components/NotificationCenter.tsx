'use client'

import { useState, useEffect, useRef } from 'react'
import { useCustomerStore } from '@/stores/customerStore'
import { Bell, BellOff, Trash2 } from 'lucide-react'
import { motion, AnimatePresence, useMotionValue, animate } from 'framer-motion'

interface NotificationCardProps {
  n: any
  onRead: () => void
  onDelete: () => void
}

function NotificationCard({ n, onRead, onDelete }: NotificationCardProps) {
  const x = useMotionValue(0)
  
  // Drag threshold in pixels (swiping left past -100px triggers delete)
  const threshold = -100

  const handleDragEnd = () => {
    const currentX = x.get()
    if (currentX < threshold) {
      onDelete()
    } else {
      // Force spring-back animation to return the card to the original position
      animate(x, 0, { type: 'spring', stiffness: 500, damping: 30 })
    }
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ 
        x: -360, 
        opacity: 0, 
        height: 0, 
        paddingTop: 0, 
        paddingBottom: 0, 
        marginTop: 0, 
        marginBottom: 0,
        transition: { duration: 0.2, ease: 'easeOut' }
      }}
      transition={{ type: 'spring', stiffness: 500, damping: 32 }}
      className="relative rounded-xl"
    >
      {/* Draggable Notification Card */}
      <motion.div
        drag="x"
        dragDirectionLock
        dragConstraints={{ right: 0, left: -320 }}
        dragElastic={{ right: 0.05, left: 0.6 }}
        style={{ x }}
        onDragEnd={handleDragEnd}
        onTap={() => {
          if (!n.read) {
            onRead()
          }
        }}
        className={`relative z-10 p-3.5 rounded-xl border border-l-4 cursor-grab active:cursor-grabbing select-none transition-all duration-200 ${
          n.read 
            ? 'bg-stone-50/70 border-stone-200/60 border-l-stone-300 text-stone-500 hover:bg-stone-100/70' 
            : 'bg-white hover:bg-[#F8FAF8] border-[#E2EDE7] border-l-[#84CC16] shadow-xs text-stone-900'
        }`}
      >
        <div className="flex justify-between items-start gap-2">
          <h4 className={`font-bold text-xs ${n.read ? 'text-stone-600' : 'text-stone-900'}`}>
            {n.title}
          </h4>
          {!n.read && (
            <span className="w-2 h-2 bg-[#84CC16] rounded-full flex-shrink-0 mt-1 shadow-[0_0_8px_rgba(132,204,22,0.6)]" />
          )}
        </div>
        <p className={`text-[11px] mt-1 leading-relaxed ${n.read ? 'text-stone-400' : 'text-stone-600 font-medium'}`}>
          {n.message}
        </p>
        <div className="text-[9px] text-stone-400 mt-1.5 font-medium flex items-center justify-between">
          <span>{new Date(n.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</span>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default function NotificationCenter() {
  const { 
    notifications, 
    fetchNotifications, 
    markNotificationRead, 
    markAllNotificationsRead,
    deleteNotification
  } = useCustomerStore()
  const [isOpen, setIsOpen] = useState(false)
  const [isClearing, setIsClearing] = useState(false)

  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchNotifications()
    const timer = setInterval(() => {
      fetchNotifications()
    }, 15000) // poll every 15s
    return () => clearInterval(timer)
  }, [fetchNotifications])

  useEffect(() => {
    function handleClickOutside(event: MouseEvent | TouchEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('touchstart', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('touchstart', handleClickOutside)
    }
  }, [])

  const unreadCount = notifications.filter((n) => !n.read).length

  const handleClearAll = async () => {
    if (isClearing || notifications.length === 0) return
    setIsClearing(true)
    try {
      await Promise.all(notifications.map((n) => deleteNotification(n.id)))
    } catch (e) {
      console.error('Failed to clear notifications:', e)
    } finally {
      setIsClearing(false)
    }
  }

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-stone-600 hover:text-stone-900 transition-colors duration-200 focus:outline-none"
        title="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 bg-[#84CC16] text-[#0B0F0D] text-[9px] font-black rounded-full w-4 h-4 flex items-center justify-center animate-bounce shadow-[0_2px_8px_rgba(132,204,22,0.4)]">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Transparent Click-Outside Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-transparent" 
          onClick={() => setIsOpen(false)} 
        />
      )}

      {isOpen && (
        <div className="absolute top-full right-0 w-[350px] mt-2 bg-[#FAFBF9] shadow-[0_25px_60px_-15px_rgba(22,29,26,0.30)] rounded-2xl border-2 border-[#E2EDE7] p-4 z-50 max-h-[440px] overflow-y-auto scrollbar-thin scrollbar-thumb-stone-300 scrollbar-track-transparent animate-in fade-in slide-in-from-top-2 duration-150 flex flex-col gap-3">
          <div className="flex justify-between items-center pb-2.5 border-b border-stone-100">
            <h3 className="font-extrabold text-stone-900 text-sm flex items-center gap-1.5">
              Notifications
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 text-[9px] font-black bg-[#84CC16]/20 text-[#365314] border border-[#84CC16]/40 rounded-full">
                  {unreadCount} New
                </span>
              )}
            </h3>
            <div className="flex items-center gap-3">
              {unreadCount > 0 && (
                <button
                  onClick={() => markAllNotificationsRead()}
                  className="text-[11px] font-bold text-[#4D7C0F] hover:text-[#365314] transition-colors"
                >
                  Mark read
                </button>
              )}
              {notifications.length > 0 && (
                <button
                  onClick={handleClearAll}
                  disabled={isClearing}
                  className="text-[11px] font-bold text-stone-500 hover:text-red-600 transition-colors flex items-center gap-1"
                  title="Clear all notifications"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>Clear all</span>
                </button>
              )}
            </div>
          </div>

          {notifications.length === 0 ? (
            <div className="text-center py-8 text-stone-400 text-xs">
              <BellOff className="w-8 h-8 mx-auto mb-2 opacity-40 text-stone-400" />
              <p className="font-semibold text-stone-600">No notifications yet</p>
              <p className="text-[10px] text-stone-400 mt-0.5">Project and execution updates will appear here</p>
            </div>
          ) : (
            <>
              <div className="space-y-2 flex-1 max-h-[300px] overflow-y-auto pr-1">
                <AnimatePresence initial={false}>
                  {notifications.map((n) => (
                    <NotificationCard
                      key={n.id}
                      n={n}
                      onRead={() => markNotificationRead(n.id)}
                      onDelete={() => deleteNotification(n.id)}
                    />
                  ))}
                </AnimatePresence>
              </div>
              <div className="text-[10px] text-stone-400 text-center pt-2 mt-1 border-t border-stone-100 select-none font-medium">
                Swipe left on a card to delete
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
