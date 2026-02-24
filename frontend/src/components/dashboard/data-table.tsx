'use client'

import type { ReactNode } from 'react'

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'

export interface Column<T> {
  key: string
  header: string
  cell: (row: T, index: number) => ReactNode
  className?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  skeletonRows?: number
  emptyMessage?: string
  onRowClick?: (row: T) => void
  rowKey: (row: T) => string
}

export function DataTable<T>({
  columns,
  data,
  loading = false,
  skeletonRows = 5,
  emptyMessage = 'No data found',
  onRowClick,
  rowKey
}: DataTableProps<T>) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map(col => (
              <TableHead key={col.key} className={col.className}>
                {col.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {loading
            ? Array.from({ length: skeletonRows }).map((_, i) => (
                <TableRow key={i}>
                  {columns.map(col => (
                    <TableCell key={col.key}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            : data.length === 0
              ? (
                  <TableRow>
                    <TableCell colSpan={columns.length} className="py-8 text-center text-sm text-muted-foreground">
                      {emptyMessage}
                    </TableCell>
                  </TableRow>
                )
              : data.map((row, i) => (
                  <TableRow
                    key={rowKey(row)}
                    className={onRowClick ? 'cursor-pointer' : undefined}
                    onClick={() => onRowClick?.(row)}
                  >
                    {columns.map(col => (
                      <TableCell key={col.key} className={col.className}>
                        {col.cell(row, i)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
        </TableBody>
      </Table>
    </div>
  )
}
