'use client'

import { useEffect, useState } from 'react'

import { Check, Copy, Eye, EyeOff, Key, Loader2, Play, Plus, RefreshCw, Server, Shield, Star, Trash2, Zap } from 'lucide-react'
import { useTheme } from 'next-themes'

import type { APIKeyCreatedResponse, APIKeyResponse, OrganizationResponse, ProviderResponse, ProviderTestResponse } from '@/types/api'
import { PROVIDER_TYPES } from '@/types/api'
import { checkApiHealth, clearStoredApiKey, setStoredApiKey } from '@/lib/api/client'
import {
  createApiKey,
  createOrganization,
  fetchApiKeys,
  fetchOrganization,
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

export function SettingsPage() {
  const { theme, setTheme } = useTheme()

  // ─── Organization ───
  const [orgId, setOrgId] = useState<string>('')
  const [orgLoading, setOrgLoading] = useState(false)
  const [org, setOrg] = useState<OrganizationResponse | null>(null)
  const [orgError, setOrgError] = useState<string | null>(null)

  // ─── Create Org ───
  const [showCreateOrg, setShowCreateOrg] = useState(false)
  const [newOrgName, setNewOrgName] = useState('')
  const [newOrgSlug, setNewOrgSlug] = useState('')
  const [newOrgDesc, setNewOrgDesc] = useState('')
  const [createOrgLoading, setCreateOrgLoading] = useState(false)

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

  const loadOrg = async (id: string) => {
    setOrgLoading(true)
    setOrgError(null)
    const res = await fetchOrganization(id)

    if (res.data) {
      setOrg(res.data)
      loadKeys(id)
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

  useEffect(() => {
    const stored = localStorage.getItem(ORG_ID_KEY)

    if (stored) {
      setOrgId(stored)
      loadOrg(stored)
    }

    // Load active API key prefix for display
    const storedKey = localStorage.getItem(API_KEY_STORAGE_KEY)

    if (storedKey) {
      setActiveKeyPrefix(storedKey.slice(0, 12) + '...')
    }

    loadProviders()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleConnectOrg = () => {
    if (!orgId.trim()) return
    localStorage.setItem(ORG_ID_KEY, orgId.trim())
    loadOrg(orgId.trim())
  }

  const handleCreateOrg = async () => {
    if (!newOrgName.trim()) return
    setCreateOrgLoading(true)

    const res = await createOrganization({
      name: newOrgName.trim(),
      slug: newOrgSlug.trim() || undefined,
      description: newOrgDesc.trim() || undefined
    })

    if (res.data) {
      setOrg(res.data)
      setOrgId(res.data.id)
      localStorage.setItem(ORG_ID_KEY, res.data.id)
      setShowCreateOrg(false)
      setNewOrgName('')
      setNewOrgSlug('')
      setNewOrgDesc('')
      loadKeys(res.data.id)
    }

    setCreateOrgLoading(false)
  }

  const handleCreateKey = async () => {
    if (!newKeyName.trim() || !org) return
    setCreateKeyLoading(true)
    const res = await createApiKey(org.id, { name: newKeyName.trim(), scopes: newKeyScopes })

    if (res.data) {
      setCreatedKey(res.data)
      setShowCreateKey(false)
      setNewKeyName('')
      loadKeys(org.id)
    }

    setCreateKeyLoading(false)
  }

  const handleRevokeKey = async (keyId: string) => {
    if (!org) return
    await revokeApiKey(org.id, keyId)
    loadKeys(org.id)
  }

  const handleRotateKey = async (keyId: string) => {
    if (!org) return
    const res = await rotateApiKey(org.id, keyId)

    if (res.data) {
      setCreatedKey(res.data)
      loadKeys(org.id)
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
            <Badge key={s} variant="secondary" className="text-[10px]">
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
              <p className="text-[11px] text-muted-foreground">
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
              <CardTitle className="text-sm">Organization</CardTitle>
              <CardDescription>Connect to or create an organization</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={() => setShowCreateOrg(true)}>
              <Plus className="mr-1 size-3" /> Create Organization
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {org ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{org.name}</p>
                  <p className="text-xs text-muted-foreground">Slug: {org.slug}</p>
                </div>
                <StatusBadge variant={org.is_active ? 'success' : 'error'}>
                  {org.is_active ? 'Active' : 'Inactive'}
                </StatusBadge>
              </div>
              {org.description && <p className="text-sm text-muted-foreground">{org.description}</p>}
              <p className="text-[11px] text-muted-foreground">ID: {org.id}</p>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Input
                placeholder="Organization ID"
                value={orgId}
                onChange={e => setOrgId(e.target.value)}
                className="max-w-xs"
              />
              <Button variant="outline" size="sm" onClick={handleConnectOrg} disabled={orgLoading}>
                {orgLoading ? 'Loading...' : 'Connect'}
              </Button>
            </div>
          )}
          {orgError && <p className="text-xs text-destructive">{orgError}</p>}
        </CardContent>
      </Card>

      {/* API Keys */}
      {org && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Key className="size-4" /> API Keys
                </CardTitle>
                <CardDescription>Manage API keys for {org.name}</CardDescription>
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

      {/* Create Org dialog */}
      <Dialog open={showCreateOrg} onOpenChange={setShowCreateOrg}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Organization</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1">
              <Label>Name *</Label>
              <Input value={newOrgName} onChange={e => setNewOrgName(e.target.value)} placeholder="My Organization" />
            </div>
            <div className="space-y-1">
              <Label>Slug</Label>
              <Input value={newOrgSlug} onChange={e => setNewOrgSlug(e.target.value)} placeholder="my-org" />
              <p className="text-[11px] text-muted-foreground">Lowercase, hyphens only. Auto-generated if empty.</p>
            </div>
            <div className="space-y-1">
              <Label>Description</Label>
              <Input value={newOrgDesc} onChange={e => setNewOrgDesc(e.target.value)} placeholder="Optional description" />
            </div>
            <Button onClick={handleCreateOrg} disabled={createOrgLoading || !newOrgName.trim()}>
              {createOrgLoading ? 'Creating...' : 'Create'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

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
                        <Badge variant="secondary" className="text-[10px]">{p.provider_type}</Badge>
                        {p.is_default && (
                          <Badge variant="outline" className="gap-1 text-[10px]">
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
              <p className="text-[11px] text-muted-foreground">Encrypted at rest. Not required for local providers (Ollama, vLLM).</p>
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
    </div>
  )
}
