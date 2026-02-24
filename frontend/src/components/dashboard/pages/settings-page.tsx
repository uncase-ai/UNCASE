'use client'

import { useEffect, useState } from 'react'

import { Check, Copy, Eye, EyeOff, Key, Plus, RefreshCw, Shield, Trash2 } from 'lucide-react'
import { useTheme } from 'next-themes'

import type { APIKeyCreatedResponse, APIKeyResponse, OrganizationResponse } from '@/types/api'
import { checkApiHealth } from '@/lib/api/client'
import {
  createApiKey,
  createOrganization,
  fetchApiKeys,
  fetchOrganization,
  revokeApiKey,
  rotateApiKey
} from '@/lib/api/organizations'
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

  // ─── API Health ───
  const [apiOk, setApiOk] = useState<boolean | null>(null)
  const [testLoading, setTestLoading] = useState(false)

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
                <Shield className="size-4 text-amber-500" /> API Key Created
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
                  {copiedKey ? <Check className="size-4 text-emerald-500" /> : <Copy className="size-4" />}
                </Button>
              </div>
              <div className="text-xs text-muted-foreground">
                <p>Name: {createdKey.name}</p>
                <p>Scopes: {createdKey.scopes}</p>
              </div>
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
    </div>
  )
}
