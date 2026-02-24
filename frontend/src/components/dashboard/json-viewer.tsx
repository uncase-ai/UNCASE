'use client'

import { useState } from 'react'

import { Check, ChevronDown, ChevronRight, Copy } from 'lucide-react'

import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

interface JsonViewerProps {
  data: unknown
  maxHeight?: string
  collapsible?: boolean
  className?: string
}

export function JsonViewer({ data, maxHeight = '400px', collapsible = true, className }: JsonViewerProps) {
  const [copied, setCopied] = useState(false)
  const formatted = JSON.stringify(data, null, 2)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(formatted)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={cn('relative rounded-md border bg-muted/30', className)}>
      <div className="absolute right-2 top-2 z-10">
        <Button variant="ghost" size="icon" className="size-7" onClick={handleCopy}>
          {copied ? <Check className="size-3.5 text-emerald-500" /> : <Copy className="size-3.5" />}
        </Button>
      </div>
      <pre
        className="overflow-auto p-4 font-mono text-xs leading-relaxed"
        style={{ maxHeight }}
      >
        {collapsible ? <CollapsibleJson data={data} depth={0} /> : formatted}
      </pre>
    </div>
  )
}

function CollapsibleJson({ data, depth }: { data: unknown; depth: number }) {
  const [collapsed, setCollapsed] = useState(depth > 2)

  if (data === null) return <span className="text-muted-foreground">null</span>
  if (typeof data === 'boolean') return <span className="text-amber-600 dark:text-amber-400">{String(data)}</span>
  if (typeof data === 'number') return <span className="text-blue-600 dark:text-blue-400">{data}</span>
  if (typeof data === 'string') return <span className="text-emerald-600 dark:text-emerald-400">&quot;{data}&quot;</span>

  if (Array.isArray(data)) {
    if (data.length === 0) return <span>{'[]'}</span>

    if (collapsed) {
      return (
        <span className="cursor-pointer" onClick={() => setCollapsed(false)}>
          <ChevronRight className="inline size-3" /> Array({data.length})
        </span>
      )
    }

    return (
      <span>
        <span className="cursor-pointer" onClick={() => setCollapsed(true)}>
          <ChevronDown className="inline size-3" />
        </span>
        {'[\n'}
        {data.map((item, i) => (
          <span key={i}>
            {'  '.repeat(depth + 1)}
            <CollapsibleJson data={item} depth={depth + 1} />
            {i < data.length - 1 ? ',\n' : '\n'}
          </span>
        ))}
        {'  '.repeat(depth)}{']'}
      </span>
    )
  }

  if (typeof data === 'object') {
    const entries = Object.entries(data as Record<string, unknown>)

    if (entries.length === 0) return <span>{'{}'}</span>

    if (collapsed) {
      return (
        <span className="cursor-pointer" onClick={() => setCollapsed(false)}>
          <ChevronRight className="inline size-3" /> {'{'}...{'}'}
        </span>
      )
    }

    return (
      <span>
        <span className="cursor-pointer" onClick={() => setCollapsed(true)}>
          <ChevronDown className="inline size-3" />
        </span>
        {'{\n'}
        {entries.map(([key, val], i) => (
          <span key={key}>
            {'  '.repeat(depth + 1)}
            <span className="text-violet-600 dark:text-violet-400">&quot;{key}&quot;</span>
            {': '}
            <CollapsibleJson data={val} depth={depth + 1} />
            {i < entries.length - 1 ? ',\n' : '\n'}
          </span>
        ))}
        {'  '.repeat(depth)}{'}'}
      </span>
    )
  }

  return <span>{String(data)}</span>
}
