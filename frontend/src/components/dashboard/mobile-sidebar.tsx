'use client'

import { Sheet, SheetContent, SheetTitle } from '@/components/ui/sheet'

import { Sidebar } from './sidebar'

interface MobileSidebarProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function MobileSidebar({ open, onOpenChange }: MobileSidebarProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-56 p-0">
        <SheetTitle className="sr-only">Navigation</SheetTitle>
        <Sidebar collapsed={false} onNavigate={() => onOpenChange(false)} />
      </SheetContent>
    </Sheet>
  )
}
