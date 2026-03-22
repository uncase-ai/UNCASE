'use client'

import { useEffect, useState } from 'react'

import { Building2, Check, Copy, Crown, Eye, EyeOff, Key, Link2, Loader2, Play, Plus, RefreshCw, Server, Shield, ShieldOff, Star, Trash2, UserIcon, Users, X, Zap } from 'lucide-react'
import { useTheme } from 'next-themes'

import type { APIKeyCreatedResponse, APIKeyResponse, BlockchainStats, OrgDetailResponse, OrgMemberResponse, ProviderResponse, ProviderTestResponse } from '@/types/api'
import { PROVIDER_TYPES } from '@/types/api'
import { useAuth } from '@/contexts/auth-context'
import { getMyOrganization, getOrgMembers } from '@/lib/api/auth'
import { checkApiHealth, clearStoredApiKey, setStoredApiKey } from '@/lib/api/client'
import { fetchBlockchainStats } from '@/lib/api/blockchain'
import {
  createApiKey,
  fetchApiKeys,
  revokeApiKey,
  rotateApiKey
} from '@/lib/api/organizations'
import {
  createProvider,
  deleteProvider,
  fetchProviders,
  testProvider
} from '@/lib/api/providers'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'

import type { Column } from '../data-table'
import { DataTable } from '../data-table'
import { PageHeader } from '../page-header'
import { StatusBadge } from '../status-badge'

const ORG_ID_KEY = 'uncase-org-id'
const API_KEY_STORAGE_KEY = 'uncase-api-key'
const BYPASS_WORDS_KEY = 'uncase-bypass-words'

function loadBypassWords(): string[] {
  if (typeof window === 'undefined') return []

  try {
    const raw = localStorage.getItem(BYPASS_WORDS_KEY)

    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveBypassWords(words: string[]) {
  localStorage.setItem(BYPASS_WORDS_KEY, JSON.stringify(words))
}

export { loadBypassWords }

const ROLE_LABELS: Record<string, string> = {
  owner: 'Owner',
  admin: 'Admin',
  member: 'Member',
  viewer: 'Viewer'
}

const ROLE_VARIANTS: Record<string, 'default' | 'success' | 'warning' | 'info' | 'error'> = {
  owner: 'success',
  admin: 'info',
  member: 'default',
  viewer: 'warning'
}

export function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const { user, isOpenMode } = useAuth()

  // ─── Organization ───
  const [orgDetail, setOrgDetail] = useState<OrgDetailResponse | null>(null)
  const [orgLoading, setOrgLoading] = useState(false)
  const [orgError, setOrgError] = useState<string | null>(null)
  const [members, setMembers] = useState<OrgMemberResponse[]>([])
  const [membersLoading, setMembersLoading] = useState(false)

  // ─── API Keys ───
  const [keys, setKeys] = useState<APIKeyResponse[]>([])
  const [keysLoading, setKeysLoading] = useState(false)
  const [showCreateKey, setShowCreateKey] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyScopes, setNewKeyScopes] = useState('read')
  const [createKeyLoading, setCreateKeyLoading] = useState(false)
  const [createdKey, setCreatedKey] = useState<APIKeyCreatedResponse | null>(null)
  const [showKey, setShowKey] = useState(false)
  const [copiedKey, setCopiedKey] = useState(false)

  // ─── Active API Key ───
  const [activeKeyPrefix, setActiveKeyPrefix] = useState<string | null>(null)

  // ─── Bypass Words ───
  const [bypassWords, setBypassWords] = useState<string[]>(() => loadBypassWords())
  const [newBypassWord, setNewBypassWord] = useState('')

  // ─── API Health ───
  const [apiOk, setApiOk] = useState<boolean | null>(null)
  const [testLoading, setTestLoading] = useState(false)

  // ─── Providers ───
  const [providers, setProviders] = useState<ProviderResponse[]>([])
  const [providersLoading, setProvidersLoading] = useState(false)
  const [showCreateProvider, setShowCreateProvider] = useState(false)
  const [createProviderLoading, setCreateProviderLoading] = useState(false)
  const [providerTest, setProviderTest] = useState<Record<string, ProviderTestResponse | 'loading'>>({})

  const [newProvider, setNewProvider] = useState({
    name: '',
    provider_type: 'anthropic' as string,
    api_key: '',
    api_base: '',
    default_model: '',
    is_default: false
  })

  // ─── Blockchain Config ───
  const [bcStats, setBcStats] = useState<BlockchainStats | null>(null)
  const [bcLoading, setBcLoading] = useState(false)

  const loadBlockchainStatus = async () => {
    setBcLoading(true)
    const res = await fetchBlockchainStats()

    if (res.data) setBcStats(res.data)
    setBcLoading(false)
  }

  const loadProviders = async () => {
    setProvidersLoading(true)
    const res = await fetchProviders(false)

    if (res.data) setProviders(res.data.items)
    setProvidersLoading(false)
  }

  const handleCreateProvider = async () => {
    if (!newProvider.name.trim() || !newProvider.default_model.trim()) return
    setCreateProviderLoading(true)

    const res = await createProvider({
      name: newProvider.name.trim(),
      provider_type: newProvider.provider_type as (typeof PROVIDER_TYPES)[number],
      api_key: newProvider.api_key.trim() || undefined,
      api_base: newProvider.api_base.trim() || undefined,
      default_model: newProvider.default_model.trim(),
      is_default: newProvider.is_default
    })

    if (res.data) {
      setShowCreateProvider(false)
      setNewProvider({ name: '', provider_type: 'anthropic', api_key: '', api_base: '', default_model: '', is_default: false })
      loadProviders()
    }

    setCreateProviderLoading(false)
  }

  const handleDeleteProvider = async (id: string) => {
    await deleteProvider(id)
    loadProviders()
  }

  const handleTestProvider = async (id: string) => {
    setProviderTest(prev => ({ ...prev, [id]: 'loading' }))
    const res = await testProvider(id)

    if (res.data) {
      setProviderTest(prev => ({ ...prev, [id]: res.data! }))
    } else {
      setProviderTest(prev => ({ ...prev, [id]: { provider_id: id, provider_name: '', status: 'error', latency_ms: null, model_tested: '', error: res.error?.message ?? 'Test failed' } }))
    }
  }

  const MODEL_HINTS: Record<string, string> = {
    anthropic: 'claude-sonnet-4-20250514',
    openai: 'gpt-4o',
    google: 'gemini-2.0-flash',
    ollama: 'llama3.1:8b',
    vllm: 'meta-llama/Llama-3.1-8B',
    groq: 'llama-3.1-8b-instant',
    custom: 'model-name'
  }

  const loadOrgDetail = async () => {
    setOrgLoading(true)
    setOrgError(null)
    const res = await getMyOrganization()

    if (res.data) {
      setOrgDetail(res.data)
      localStorage.setItem(ORG_ID_KEY, res.data.id)
      loadKeys(res.data.id)

      // Load members if user is owner/admin
      if (res.data.role === 'owner' || res.data.role === 'admin') {
        loadMembers()
      }
    } else {
      setOrgError(res.error?.message ?? 'Failed to load organization')
    }

    setOrgLoading(false)
  }

  const loadKeys = async (id: string) => {
    setKeysLoading(true)
    const res = await fetchApiKeys(id)

    if (res.data) setKeys(res.data)
    setKeysLoading(false)
  }

  const loadMembers = async () => {
    setMembersLoading(true)
    const res = await getOrgMembers()

    if (res.data) setMembers(res.data.members)
    setMembersLoading(false)
  }

  useEffect(() => {
    // Load org details via Bearer token (not API key)
    if (user && !isOpenMode) {
      loadOrgDetail()
    }

    // Load active API key prefix for display
    const storedKey = localStorage.getItem(API_KEY_STORAGE_KEY)

    if (storedKey) {
      setActiveKeyPrefix(storedKey.slice(0, 12) + '...')
    }

    loadProviders()
    loadBlockchainStatus()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleCreateKey = async () => {
    if (!newKeyName.trim() || !orgDetail) return
    setCreateKeyLoading(true)
    const res = await createApiKey(orgDetail.id, { name: newKeyName.trim(), scopes: newKeyScopes })

    if (res.data) {
      setCreatedKey(res.data)
      setShowCreateKey(false)
      setNewKeyName('')
      loadKeys(orgDetail.id)
    }

    setCreateKeyLoading(false)
  }

  const handleRevokeKey = async (keyId: string) => {
    if (!orgDetail) return
    await revokeApiKey(orgDetail.id, keyId)
    loadKeys(orgDetail.id)
  }

  const handleRotateKey = async (keyId: string) => {
    if (!orgDetail) return
    const res = await rotateApiKey(orgDetail.id, keyId)

    if (res.data) {
      setCreatedKey(res.data)
      loadKeys(orgDetail.id)
    }
  }

  const handleTestApi = async () => {
    setTestLoading(true)
    const ok = await checkApiHealth()

    setApiOk(ok)
    setTestLoading(false)
  }

  const copyKey = async (key: string) => {
    await navigator.clipboard.writeText(key)
    setCopiedKey(true)
    setTimeout(() => setCopiedKey(false), 2000)
  }

  const handleAddBypassWord = () => {
    const word = newBypassWord.trim()

    if (!word || bypassWords.some(w => w.toLowerCase() === word.toLowerCase())) return

    const updated = [...bypassWords, word]

    setBypassWords(updated)
    saveBypassWords(updated)
    setNewBypassWord('')
  }

  const handleRemoveBypassWord = (word: string) => {
    const updated = bypassWords.filter(w => w !== word)

    setBypassWords(updated)
    saveBypassWords(updated)
  }

  const keyColumns: Column<APIKeyResponse>[] = [
    {
      key: 'name',
      header: 'Name',
      cell: row => <span className="font-medium">{row.name}</span>
    },
    {
      key: 'prefix',
      header: 'Key',
      cell: row => <code className="text-xs">{row.key_prefix}...</code>
    },
    {
      key: 'scopes',
      header: 'Scopes',
      cell: row => (
        <div className="flex gap-1">
          {row.scopes.split(',').map(s => (
            <Badge key={s} variant="secondary" className="text-xs">
              {s.trim()}
            </Badge>
          ))}
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      cell: row => (
        <StatusBadge variant={row.is_active ? 'success' : 'error'}>
          {row.is_active ? 'Active' : 'Revoked'}
        </StatusBadge>
      )
    },
    {
      key: 'created',
      header: 'Created',
      cell: row => <span className="text-xs text-muted-foreground">{new Date(row.created_at).toLocaleDateString()}</span>
    },
    {
      key: 'actions',
      header: '',
      cell: row =>
        row.is_active ? (
          <div className="flex gap-1">
            <Button variant="ghost" size="icon" className="size-7" onClick={() => handleRotateKey(row.key_id)} title="Rotate">
              <RefreshCw className="size-3" />
            </Button>
            <Button variant="ghost" size="icon" className="size-7 text-destructive" onClick={() => handleRevokeKey(row.key_id)} title="Revoke">
              <Trash2 className="size-3" />
            </Button>
          </div>
        ) : null
    }
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" description="Organization, API keys, and preferences" />

      <div className="grid gap-6 lg:grid-cols-2">
        {/* API Connection */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">API Connection</CardTitle>
            <CardDescription>Test connectivity to the UNCASE backend</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <code className="flex-1 rounded bg-muted px-3 py-2 text-xs">
                {process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}
              </code>
              <Button variant="outline" size="sm" onClick={handleTestApi} disabled={testLoading}>
                {testLoading ? 'Testing...' : 'Test'}
              </Button>
            </div>
            {apiOk !== null && (
              <StatusBadge variant={apiOk ? 'success' : 'error'}>
                {apiOk ? 'Connected' : 'Unreachable'}
              </StatusBadge>
            )}
            {activeKeyPrefix ? (
              <div className="flex items-center justify-between rounded border border-green-200 bg-green-50 px-3 py-2 dark:border-green-900 dark:bg-green-950">
                <div className="flex items-center gap-2 text-xs">
                  <Key className="size-3 text-green-600 dark:text-green-400" />
                  <span className="text-green-700 dark:text-green-300">Active key: <code>{activeKeyPrefix}</code></span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 text-xs text-destructive"
                  onClick={() => {
                    clearStoredApiKey()
                    setActiveKeyPrefix(null)
                  }}
                >
                  Clear
                </Button>
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">
                No API key active. Create one below and set it as active to authenticate requests.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Theme & Appearance */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Appearance</CardTitle>
            <CardDescription>Theme and display preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Theme</Label>
              <Select value={theme ?? 'system'} onValueChange={setTheme}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </div>

      <Separator />

      {/* Organization */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Building2 className="size-4" /> Organization
              </CardTitle>
              <CardDescription>
                {orgDetail ? 'Your organization details and membership' : 'Organization membership'}
              </CardDescription>
            </div>
            {orgDetail && (
              <StatusBadge variant={ROLE_VARIANTS[orgDetail.role] ?? 'default'}>
                {ROLE_LABELS[orgDetail.role] ?? orgDetail.role}
              </StatusBadge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {orgLoading ? (
            <div className="flex items-center gap-2 py-4 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" /> Loading organization...
            </div>
          ) : orgDetail ? (
            <div className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg border px-4 py-3">
                  <p className="text-xs font-medium uppercase text-muted-foreground">Name</p>
                  <p className="text-sm font-medium">{orgDetail.name}</p>
                </div>
                <div className="rounded-lg border px-4 py-3">
                  <p className="text-xs font-medium uppercase text-muted-foreground">Slug</p>
                  <p className="text-sm font-mono">{orgDetail.slug}</p>
                </div>
                <div className="rounded-lg border px-4 py-3">
                  <p className="text-xs font-medium uppercase text-muted-foreground">Members</p>
                  <p className="text-sm font-medium">{orgDetail.member_count}</p>
                </div>
                <div className="rounded-lg border px-4 py-3">
                  <p className="text-xs font-medium uppercase text-muted-foreground">Status</p>
                  <StatusBadge variant={orgDetail.is_active ? 'success' : 'error'}>
                    {orgDetail.is_active ? 'Active' : 'Inactive'}
                  </StatusBadge>
                </div>
              </div>
              {orgDetail.description && (
                <p className="text-sm text-muted-foreground">{orgDetail.description}</p>
              )}
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>ID: <code>{orgDetail.id}</code></span>
                <span>·</span>
                <span>Your role: <strong>{ROLE_LABELS[orgDetail.role] ?? orgDetail.role}</strong></span>
              </div>
            </div>
          ) : isOpenMode ? (
            <div className="py-4 text-center text-sm text-muted-foreground">
              Running in open mode (no organization). Register an account to create an organization.
            </div>
          ) : (
            <div className="py-4 text-center text-sm text-muted-foreground">
              {orgError ? (
                <p className="text-destructive">{orgError}</p>
              ) : (
                'No organization found. Contact your administrator.'
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Members — only for owner/admin */}
      {orgDetail && (orgDetail.role === 'owner' || orgDetail.role === 'admin') && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Users className="size-4" /> Members
                </CardTitle>
                <CardDescription>People in {orgDetail.name}</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {membersLoading ? (
              <div className="flex items-center gap-2 py-4 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" /> Loading members...
              </div>
            ) : members.length === 0 ? (
              <p className="py-4 text-center text-sm text-muted-foreground">No members found.</p>
            ) : (
              <div className="space-y-2">
                {members.map(member => (
                  <div key={member.user_id} className="flex items-center justify-between rounded-lg border px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex size-8 items-center justify-center rounded-full bg-muted">
                        {member.role === 'owner' ? (
                          <Crown className="size-4 text-amber-500" />
                        ) : (
                          <UserIcon className="size-4 text-muted-foreground" />
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{member.display_name}</p>
                        <p className="text-xs text-muted-foreground">{member.email}</p>
                      </div>
                    </div>
                    <StatusBadge variant={ROLE_VARIANTS[member.role] ?? 'default'}>
                      {ROLE_LABELS[member.role] ?? member.role}
                    </StatusBadge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* API Keys — only for owner/admin */}
      {orgDetail && (orgDetail.role === 'owner' || orgDetail.role === 'admin') && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Key className="size-4" /> API Keys
                </CardTitle>
                <CardDescription>Manage API keys for {orgDetail.name}</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={() => setShowCreateKey(true)}>
                <Plus className="mr-1 size-3" /> Create Key
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={keyColumns}
              data={keys}
              loading={keysLoading}
              rowKey={r => r.key_id}
              emptyMessage="No API keys. Create one to authenticate API requests."
            />
          </CardContent>
        </Card>
      )}

      {/* Created key alert */}
      {createdKey && (
        <Dialog open={!!createdKey} onOpenChange={() => setCreatedKey(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Shield className="size-4" /> API Key Created
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Copy this key now. It will not be shown again.
              </p>
              <div className="flex items-center gap-2">
                <code className="flex-1 break-all rounded bg-muted px-3 py-2 text-xs">
                  {showKey ? createdKey.plain_key : '••••••••••••••••••••••••••••••••'}
                </code>
                <Button variant="ghost" size="icon" className="size-8" onClick={() => setShowKey(!showKey)}>
                  {showKey ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                </Button>
                <Button variant="ghost" size="icon" className="size-8" onClick={() => copyKey(createdKey.plain_key)}>
                  {copiedKey ? <Check className="size-4" /> : <Copy className="size-4" />}
                </Button>
              </div>
              <div className="text-xs text-muted-foreground">
                <p>Name: {createdKey.name}</p>
                <p>Scopes: {createdKey.scopes}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => {
                  setStoredApiKey(createdKey.plain_key)
                  setActiveKeyPrefix(createdKey.plain_key.slice(0, 12) + '...')
                  setCreatedKey(null)
                }}
              >
                <Key className="mr-1 size-3" /> Set as Active Key for API Requests
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Create Key dialog */}
      <Dialog open={showCreateKey} onOpenChange={setShowCreateKey}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create API Key</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1">
              <Label>Name *</Label>
              <Input value={newKeyName} onChange={e => setNewKeyName(e.target.value)} placeholder="Production Key" />
            </div>
            <div className="space-y-1">
              <Label>Scopes</Label>
              <Select value={newKeyScopes} onValueChange={setNewKeyScopes}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="read">Read</SelectItem>
                  <SelectItem value="read,write">Read + Write</SelectItem>
                  <SelectItem value="read,write,admin">Admin (full access)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={handleCreateKey} disabled={createKeyLoading || !newKeyName.trim()}>
              {createKeyLoading ? 'Creating...' : 'Create Key'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Separator />

      {/* Bypass Words */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-sm">
                <ShieldOff className="size-4" /> Bypassed Words
              </CardTitle>
              <CardDescription>
                Words excluded from PII detection (e.g., bot names, place names, holidays). These words will not be flagged
                or anonymized when scanning conversations through the LLM Gateway.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <Input
              placeholder="Add a word (e.g., Mariana, Christmas, Tokyo)"
              value={newBypassWord}
              onChange={e => setNewBypassWord(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter') handleAddBypassWord()
              }}
              className="max-w-sm"
            />
            <Button variant="outline" size="sm" onClick={handleAddBypassWord} disabled={!newBypassWord.trim()}>
              <Plus className="mr-1 size-3" /> Add
            </Button>
          </div>
          {bypassWords.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {bypassWords.map(word => (
                <Badge key={word} variant="secondary" className="gap-1 pr-1 text-xs">
                  {word}
                  <button
                    onClick={() => handleRemoveBypassWord(word)}
                    className="ml-1 rounded-full p-0.5 hover:bg-muted-foreground/20"
                  >
                    <X className="size-3" />
                  </button>
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">
              No bypassed words configured. Add words that should be excluded from PII checks, such as bot names
              (&quot;Mariana&quot;), place names, holiday names, or domain-specific terms.
            </p>
          )}
        </CardContent>
      </Card>

      <Separator />

      {/* LLM Providers */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Server className="size-4" /> LLM Providers
              </CardTitle>
              <CardDescription>Configure language model providers for synthetic data generation</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={() => setShowCreateProvider(true)}>
              <Plus className="mr-1 size-3" /> Add Provider
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {providersLoading ? (
            <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
              <Loader2 className="mr-2 size-4 animate-spin" /> Loading providers...
            </div>
          ) : providers.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              No providers configured. Add one to enable synthetic data generation.
            </div>
          ) : (
            <div className="space-y-3">
              {providers.map(p => {
                const test = providerTest[p.id]
                const isTestLoading = test === 'loading'
                const testResult = test && test !== 'loading' ? test : null

                return (
                  <div key={p.id} className="flex items-center gap-4 rounded-lg border px-4 py-3">
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{p.name}</span>
                        <Badge variant="secondary" className="text-xs">{p.provider_type}</Badge>
                        {p.is_default && (
                          <Badge variant="outline" className="gap-1 text-xs">
                            <Star className="size-2.5" /> Default
                          </Badge>
                        )}
                        <StatusBadge variant={p.is_active ? 'success' : 'error'}>
                          {p.is_active ? 'Active' : 'Inactive'}
                        </StatusBadge>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>Model: <code>{p.default_model}</code></span>
                        {p.has_api_key && <span className="flex items-center gap-1"><Key className="size-3" /> Key set</span>}
                        {p.api_base && <span>Base: {p.api_base}</span>}
                      </div>
                      {testResult && (
                        <div className="mt-1 flex items-center gap-2 text-xs">
                          <StatusBadge variant={testResult.status === 'ok' ? 'success' : 'error'}>
                            {testResult.status === 'ok' ? 'Connected' : 'Failed'}
                          </StatusBadge>
                          {testResult.latency_ms !== null && (
                            <span className="text-muted-foreground">{testResult.latency_ms}ms</span>
                          )}
                          {testResult.error && (
                            <span className="text-destructive">{testResult.error}</span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-7"
                        onClick={() => handleTestProvider(p.id)}
                        disabled={isTestLoading}
                        title="Test connection"
                      >
                        {isTestLoading ? <Loader2 className="size-3 animate-spin" /> : <Play className="size-3" />}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-7 text-destructive"
                        onClick={() => handleDeleteProvider(p.id)}
                        title="Delete provider"
                      >
                        <Trash2 className="size-3" />
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Provider dialog */}
      <Dialog open={showCreateProvider} onOpenChange={setShowCreateProvider}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Zap className="size-4" /> Add LLM Provider
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1">
              <Label>Name *</Label>
              <Input
                value={newProvider.name}
                onChange={e => setNewProvider(prev => ({ ...prev, name: e.target.value }))}
                placeholder="My Claude Provider"
              />
            </div>
            <div className="space-y-1">
              <Label>Provider Type *</Label>
              <Select
                value={newProvider.provider_type}
                onValueChange={v => setNewProvider(prev => ({ ...prev, provider_type: v, default_model: '' }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PROVIDER_TYPES.map(t => (
                    <SelectItem key={t} value={t}>
                      {t.charAt(0).toUpperCase() + t.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>API Key</Label>
              <Input
                type="password"
                value={newProvider.api_key}
                onChange={e => setNewProvider(prev => ({ ...prev, api_key: e.target.value }))}
                placeholder="sk-..."
              />
              <p className="text-xs text-muted-foreground">Encrypted at rest. Not required for local providers (Ollama, vLLM).</p>
            </div>
            {['ollama', 'vllm', 'custom'].includes(newProvider.provider_type) && (
              <div className="space-y-1">
                <Label>API Base URL</Label>
                <Input
                  value={newProvider.api_base}
                  onChange={e => setNewProvider(prev => ({ ...prev, api_base: e.target.value }))}
                  placeholder={newProvider.provider_type === 'ollama' ? 'http://localhost:11434' : 'http://localhost:8080/v1'}
                />
              </div>
            )}
            <div className="space-y-1">
              <Label>Default Model *</Label>
              <Input
                value={newProvider.default_model}
                onChange={e => setNewProvider(prev => ({ ...prev, default_model: e.target.value }))}
                placeholder={MODEL_HINTS[newProvider.provider_type] ?? 'model-name'}
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is-default-provider"
                checked={newProvider.is_default}
                onChange={e => setNewProvider(prev => ({ ...prev, is_default: e.target.checked }))}
                className="size-4 rounded border"
              />
              <Label htmlFor="is-default-provider" className="text-sm font-normal">
                Set as default provider
              </Label>
            </div>
            <Button
              onClick={handleCreateProvider}
              disabled={createProviderLoading || !newProvider.name.trim() || !newProvider.default_model.trim()}
              className="w-full"
            >
              {createProviderLoading ? (
                <>
                  <Loader2 className="mr-2 size-4 animate-spin" /> Creating...
                </>
              ) : (
                'Add Provider'
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Separator />

      {/* Blockchain */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Link2 className="size-4" /> Blockchain
              </CardTitle>
              <CardDescription>On-chain quality certification via Polygon PoS</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={loadBlockchainStatus} disabled={bcLoading}>
              {bcLoading ? <Loader2 className="mr-1 size-3 animate-spin" /> : <RefreshCw className="mr-1 size-3" />}
              Test Connection
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {bcStats ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <StatusBadge variant="success">Connected</StatusBadge>
                <span className="text-xs text-muted-foreground">
                  {bcStats.total_anchored} reports anchored on-chain
                </span>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg border px-3 py-2">
                  <p className="text-xs font-medium uppercase text-muted-foreground">Hashed</p>
                  <p className="text-lg font-bold">{bcStats.total_hashed}</p>
                </div>
                <div className="rounded-lg border px-3 py-2">
                  <p className="text-xs font-medium uppercase text-muted-foreground">Batches</p>
                  <p className="text-lg font-bold">{bcStats.total_batches}</p>
                </div>
                <div className="rounded-lg border px-3 py-2">
                  <p className="text-xs font-medium uppercase text-muted-foreground">Anchored</p>
                  <p className="text-lg font-bold">{bcStats.total_anchored}</p>
                </div>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-muted-foreground w-28 shrink-0">Private Key</span>
                  <StatusBadge variant={bcStats.total_anchored > 0 || bcStats.total_batches > 0 ? 'success' : 'warning'}>
                    {bcStats.total_anchored > 0 || bcStats.total_batches > 0 ? 'Configured' : 'Not configured'}
                  </StatusBadge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Blockchain settings (RPC URL, chain ID, contract address, private key) are configured via server environment variables. They cannot be modified from the UI for security reasons.
                </p>
              </div>
            </div>
          ) : (
            <div className="py-4 text-center text-sm text-muted-foreground">
              {bcLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <Loader2 className="size-4 animate-spin" /> Checking blockchain status...
                </div>
              ) : (
                'Click "Test Connection" to check blockchain configuration status.'
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
