// ─── Direct HuggingFace API wrappers (browser-side, no backend proxy) ───

import type { ApiResponse } from './client'

// ─── Types ───

export interface HFSearchResult {
  id: string
  description: string | null
  downloads: number
  likes: number
  tags: string[]
  lastModified: string
  private: boolean
  gated: boolean | string
}

export interface HFDatasetConfig {
  dataset: string
  configs: Array<{
    config_name: string
    data_files: Array<{ split: string; filename: string }>
    splits?: Array<{ name: string; num_examples?: number }>
  }>
}

export interface HFFeature {
  name: string
  type: string | Record<string, unknown>
}

export interface HFDatasetInfoResponse {
  dataset_info: Record<
    string,
    {
      config_name: string
      features: Record<string, { dtype?: string; _type?: string; feature?: unknown }>
      splits: Record<string, { name: string; num_examples: number }>
    }
  >
}

export interface HFRowsResponse {
  features: Array<{ feature_idx: number; name: string; type: { dtype?: string; _type?: string; [k: string]: unknown } }>
  rows: Array<{ row_idx: number; row: Record<string, unknown>; truncated_cells: string[] }>
  num_rows_total: number
  num_rows_per_page: number
  partial: boolean
}

// ─── API Functions ───

export async function searchDatasets(
  query: string,
  limit: number = 20,
  signal?: AbortSignal
): Promise<ApiResponse<HFSearchResult[]>> {
  try {
    const url = `https://huggingface.co/api/datasets?search=${encodeURIComponent(query)}&limit=${limit}&sort=downloads&direction=-1`
    const res = await fetch(url, { signal })

    if (!res.ok) {
      return { data: null, error: { status: res.status, message: `HF search failed: ${res.statusText}` } }
    }

    const raw: Array<Record<string, unknown>> = await res.json()
    const results: HFSearchResult[] = raw.map(d => ({
      id: d.id as string,
      description: (d.description as string) ?? null,
      downloads: (d.downloads as number) ?? 0,
      likes: (d.likes as number) ?? 0,
      tags: (d.tags as string[]) ?? [],
      lastModified: (d.lastModified as string) ?? '',
      private: (d.private as boolean) ?? false,
      gated: (d.gated as boolean | string) ?? false,
    }))

    return { data: results, error: null }
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      return { data: null, error: { status: 0, message: 'Request cancelled' } }
    }

    return { data: null, error: { status: 0, message: err instanceof Error ? err.message : 'Search failed' } }
  }
}

export async function getDatasetInfo(
  repoId: string,
  token?: string,
  signal?: AbortSignal
): Promise<ApiResponse<HFDatasetInfoResponse>> {
  try {
    const url = `https://datasets-server.huggingface.co/info?dataset=${encodeURIComponent(repoId)}`
    const headers: Record<string, string> = {}

    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(url, { signal, headers })

    if (!res.ok) {
      return { data: null, error: { status: res.status, message: `Failed to get dataset info: ${res.statusText}` } }
    }

    const data = await res.json()

    return { data: data as HFDatasetInfoResponse, error: null }
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      return { data: null, error: { status: 0, message: 'Request cancelled' } }
    }

    return { data: null, error: { status: 0, message: err instanceof Error ? err.message : 'Failed to get info' } }
  }
}

export async function getDatasetRows(
  repoId: string,
  config: string,
  split: string,
  offset: number,
  length: number,
  token?: string,
  signal?: AbortSignal
): Promise<ApiResponse<HFRowsResponse>> {
  try {
    const params = new URLSearchParams({
      dataset: repoId,
      config,
      split,
      offset: String(offset),
      length: String(length),
    })
    const url = `https://datasets-server.huggingface.co/rows?${params}`
    const headers: Record<string, string> = {}

    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(url, { signal, headers })

    if (!res.ok) {
      return { data: null, error: { status: res.status, message: `Failed to get rows: ${res.statusText}` } }
    }

    const data = await res.json()

    return { data: data as HFRowsResponse, error: null }
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      return { data: null, error: { status: 0, message: 'Request cancelled' } }
    }

    return { data: null, error: { status: 0, message: err instanceof Error ? err.message : 'Failed to get rows' } }
  }
}

export async function createHFRepo(
  repoId: string,
  token: string,
  isPrivate: boolean,
  signal?: AbortSignal
): Promise<ApiResponse<{ url: string }>> {
  try {
    const res = await fetch('https://huggingface.co/api/repos/create', {
      method: 'POST',
      signal,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: repoId.includes('/') ? repoId.split('/')[1] : repoId,
        type: 'dataset',
        private: isPrivate,
        ...(repoId.includes('/') ? { organization: repoId.split('/')[0] } : {}),
      }),
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      const message = (body as Record<string, string>).error ?? `Failed to create repo: ${res.statusText}`

      // 409 means repo already exists — treat as success
      if (res.status === 409) {
        return { data: { url: `https://huggingface.co/datasets/${repoId}` }, error: null }
      }

      return { data: null, error: { status: res.status, message } }
    }

    const data = await res.json()

    return { data: { url: (data as Record<string, string>).url ?? `https://huggingface.co/datasets/${repoId}` }, error: null }
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      return { data: null, error: { status: 0, message: 'Request cancelled' } }
    }

    return { data: null, error: { status: 0, message: err instanceof Error ? err.message : 'Failed to create repo' } }
  }
}

export async function uploadFileToHF(
  repoId: string,
  token: string,
  filename: string,
  content: string,
  signal?: AbortSignal
): Promise<ApiResponse<{ commitUrl: string }>> {
  try {
    const url = `https://huggingface.co/api/datasets/${repoId}/upload/main/${encodeURIComponent(filename)}`
    const blob = new Blob([content], { type: 'application/octet-stream' })

    const res = await fetch(url, {
      method: 'PUT',
      signal,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/octet-stream',
      },
      body: blob,
    })

    if (!res.ok) {
      const body = await res.text()

      return { data: null, error: { status: res.status, message: body || `Upload failed: ${res.statusText}` } }
    }

    return { data: { commitUrl: `https://huggingface.co/datasets/${repoId}` }, error: null }
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      return { data: null, error: { status: 0, message: 'Request cancelled' } }
    }

    return { data: null, error: { status: 0, message: err instanceof Error ? err.message : 'Upload failed' } }
  }
}
