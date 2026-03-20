'use client'

import type { ReactNode } from 'react'

interface PhoneFrameProps {
  children: ReactNode
  title?: string
}

export function PhoneFrame({ children, title = 'UNCASE' }: PhoneFrameProps) {
  return (
    <div className="mx-auto w-full max-w-sm">
      {/* Phone outer frame */}
      <div className="overflow-hidden rounded-[2.5rem] border-4 border-gray-800 bg-gray-800 shadow-2xl dark:border-zinc-600">
        {/* Notch */}
        <div className="flex items-center justify-center bg-gray-800 py-1">
          <div className="h-5 w-28 rounded-full bg-gray-900 dark:bg-zinc-800" />
        </div>

        {/* Status bar */}
        <div className="flex items-center justify-between bg-emerald-700 px-4 py-1 text-xs text-white">
          <span>9:41</span>
          <span className="font-medium">{title}</span>
          <div className="flex items-center gap-1">
            <span>●●●</span>
          </div>
        </div>

        {/* WhatsApp header */}
        <div className="flex items-center gap-3 bg-emerald-700 px-4 pb-2">
          <div className="size-8 rounded-full bg-white/20" />
          <div>
            <p className="text-sm font-semibold text-white">{title}</p>
            <p className="text-xs text-white/70">en línea</p>
          </div>
        </div>

        {/* Content */}
        <div className="h-[520px] overflow-y-auto">
          {children}
        </div>

        {/* Bottom home bar */}
        <div className="flex items-center justify-center bg-gray-800 py-2">
          <div className="h-1 w-24 rounded-full bg-gray-600" />
        </div>
      </div>
    </div>
  )
}
