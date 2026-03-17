import type { ToolDefinition } from '@/types/api'

// ─── Interfaces ───

export interface MCPServerConfig {
  serverName: string
  description: string
  tools: ToolDefinition[]
  rateLimitPerMinute: number
  corsOrigins: string[]
}

export interface MCPConnectionInfo {
  serverUrl: string
  serverSlug: string
  mcpConfig: Record<string, unknown>
  curlExample: string
  deployCommand: string
  envVars: string[]
  toolEndpoints: { name: string; method: string; url: string }[]
}

export interface MCPDeploymentPreview {
  serverName: string
  generatedCode: string
  connectionInfo: MCPConnectionInfo
  toolCount: number
  securityNotes: string[]
}

// ─── Helpers ───

function toSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function isSnakeCase(s: string): boolean {
  return /^[a-z][a-z0-9]*(_[a-z0-9]+)*$/.test(s)
}

function extractRequiredParams(schema: Record<string, unknown>): string[] {
  if (Array.isArray(schema.required)) {
    return schema.required as string[]
  }

  return []
}

function extractEnvVarsFromTools(tools: ToolDefinition[]): string[] {
  const vars = new Set<string>()

  for (const tool of tools) {
    if (!tool.requires_auth) continue

    const authType = (tool.metadata?.auth_type as string) ?? 'bearer'
    const envName = `${tool.name.toUpperCase()}_AUTH_TOKEN`

    if (authType === 'api_key') {
      vars.add(`${tool.name.toUpperCase()}_API_KEY`)
    } else if (authType === 'basic') {
      vars.add(`${tool.name.toUpperCase()}_BASIC_AUTH`)
    } else {
      vars.add(envName)
    }
  }

  return Array.from(vars)
}

function inferHttpMethod(tool: ToolDefinition): string {
  const meta = tool.metadata

  if (typeof meta?.method === 'string') {
    return meta.method.toUpperCase()
  }

  const name = tool.name.toLowerCase()

  if (name.startsWith('create_') || name.startsWith('send_') || name.startsWith('submit_')) return 'POST'
  if (name.startsWith('update_') || name.startsWith('edit_')) return 'PUT'
  if (name.startsWith('delete_') || name.startsWith('remove_')) return 'DELETE'

  return 'GET'
}

function hasCredentialInUrl(tool: ToolDefinition): boolean {
  const url = (tool.metadata?.url as string) ?? ''

  return /(?:api_key|token|secret|password|key)=/i.test(url)
}

// ─── Validation ───

export function validateToolForMCP(tool: ToolDefinition): { valid: boolean; issues: string[] } {
  const issues: string[] = []

  if (!tool.name || tool.name.trim().length === 0) {
    issues.push('Tool must have a name')
  } else if (!isSnakeCase(tool.name)) {
    issues.push(`Tool name "${tool.name}" must be snake_case (e.g. get_weather, create_order)`)
  }

  if (!tool.description || tool.description.trim().length === 0) {
    issues.push('Tool must have a description')
  }

  if (!tool.input_schema || typeof tool.input_schema !== 'object') {
    issues.push('Tool must have an input_schema object')
  } else if (tool.input_schema.type !== 'object') {
    issues.push('input_schema.type must be "object" for MCP compatibility')
  }

  if (hasCredentialInUrl(tool)) {
    issues.push('Security issue: credentials found in URL — use headers or environment variables instead')
  }

  return { valid: issues.length === 0, issues }
}

// ─── Single Tool Endpoint Generator ───

export function generateToolEndpoint(tool: ToolDefinition): string {
  const method = inferHttpMethod(tool)
  const required = extractRequiredParams(tool.input_schema)
  const authType = (tool.metadata?.auth_type as string) ?? 'bearer'
  const baseUrl = (tool.metadata?.url as string) ?? `https://api.example.com/${tool.name}`
  const envPrefix = tool.name.toUpperCase()

  const lines: string[] = []

  lines.push(`    case '${tool.name}': {`)

  // Required parameter validation
  if (required.length > 0) {
    const reqList = required.map(r => `'${r}'`).join(', ')

    lines.push(`      const requiredParams = [${reqList}]`)
    lines.push(`      const missing = requiredParams.filter(p => !(p in params))`)
    lines.push(`      if (missing.length > 0) {`)
    lines.push(`        return json({ error: \`Missing required parameters: \${missing.join(', ')}\` }, 400)`)
    lines.push(`      }`)
  }

  // Auth headers
  lines.push(`      const headers: Record<string, string> = { 'Content-Type': 'application/json' }`)

  if (tool.requires_auth) {
    if (authType === 'api_key') {
      lines.push(`      const apiKey = Deno.env.get('${envPrefix}_API_KEY')`)
      lines.push(`      if (!apiKey) return json({ error: '${envPrefix}_API_KEY not configured' }, 500)`)
      lines.push(`      headers['X-API-Key'] = apiKey`)
    } else if (authType === 'basic') {
      lines.push(`      const basicAuth = Deno.env.get('${envPrefix}_BASIC_AUTH')`)
      lines.push(`      if (!basicAuth) return json({ error: '${envPrefix}_BASIC_AUTH not configured' }, 500)`)
      lines.push(`      headers['Authorization'] = \`Basic \${basicAuth}\``)
    } else {
      lines.push(`      const token = Deno.env.get('${envPrefix}_AUTH_TOKEN')`)
      lines.push(`      if (!token) return json({ error: '${envPrefix}_AUTH_TOKEN not configured' }, 500)`)
      lines.push(`      headers['Authorization'] = \`Bearer \${token}\``)
    }
  }

  // URL construction and request
  if (method === 'GET' || method === 'DELETE') {
    lines.push(`      const qs = new URLSearchParams()`)
    lines.push(`      for (const [k, v] of Object.entries(params)) qs.set(k, String(v))`)
    lines.push(`      const url = \`${baseUrl}\${qs.toString() ? '?' + qs.toString() : ''}\``)
    lines.push(`      return proxyRequest(url, '${method}', headers)`)
  } else {
    lines.push(`      return proxyRequest('${baseUrl}', '${method}', headers, params)`)
  }

  lines.push(`    }`)

  return lines.join('\n')
}

// ─── MCP Config Generator ───

export function generateMCPConfig(tools: ToolDefinition[], serverName: string): Record<string, unknown> {
  return {
    mcpVersion: '1.0',
    server: {
      name: serverName,
      description: `MCP server wrapping ${tools.length} tool(s) from UNCASE`,
      tools: tools.map(tool => ({
        name: tool.name,
        description: tool.description,
        inputSchema: tool.input_schema,
      })),
    },
  }
}

// ─── Generated Server Code Template ───

function generateServerCode(config: MCPServerConfig): string {
  const toolCases = config.tools.map(t => generateToolEndpoint(t)).join('\n\n')

  return `// ─── UNCASE MCP Server: ${config.serverName} ───
// Auto-generated by UNCASE MCP Generator
// Deploy: supabase functions deploy ${toSlug(config.serverName)}

const RATE_LIMIT = ${config.rateLimitPerMinute}
const CORS_ORIGINS = new Set(${JSON.stringify(config.corsOrigins)})

// ─── Rate Limiter ───

const rateLimitMap = new Map<string, { count: number; resetAt: number }>()

function checkRateLimit(ip: string): boolean {
  const now = Date.now()
  const entry = rateLimitMap.get(ip)

  if (!entry || now > entry.resetAt) {
    rateLimitMap.set(ip, { count: 1, resetAt: now + 60_000 })
    return true
  }

  if (entry.count >= RATE_LIMIT) return false

  entry.count++
  return true
}

// ─── Helpers ───

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function corsHeaders(origin: string): Record<string, string> {
  const allowed = CORS_ORIGINS.has('*') || CORS_ORIGINS.has(origin)
  return {
    'Access-Control-Allow-Origin': allowed ? origin : '',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  }
}

async function proxyRequest(
  url: string,
  method: string,
  headers: Record<string, string>,
  body?: Record<string, unknown>,
): Promise<Response> {
  try {
    const init: RequestInit = { method, headers }
    if (body && method !== 'GET' && method !== 'DELETE') {
      init.body = JSON.stringify(body)
    }

    const upstream = await fetch(url, init)
    const data = await upstream.text()

    let parsed: unknown
    try {
      parsed = JSON.parse(data)
    } catch {
      parsed = { raw: data }
    }

    return json({
      status: upstream.status,
      data: parsed,
    }, upstream.ok ? 200 : 502)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown upstream error'
    return json({ error: 'Upstream request failed', detail: message }, 502)
  }
}

// ─── Handler ───

Deno.serve(async (req: Request) => {
  const url = new URL(req.url)
  const origin = req.headers.get('Origin') ?? '*'
  const cors = corsHeaders(origin)

  // CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: cors })
  }

  // Health check
  if (url.pathname === '/health' || url.pathname === '/') {
    return json({
      status: 'ok',
      server: '${config.serverName}',
      tools: ${config.tools.length},
      timestamp: new Date().toISOString(),
    })
  }

  // Rate limiting
  const clientIp = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim()
    ?? req.headers.get('cf-connecting-ip')
    ?? 'unknown'

  if (!checkRateLimit(clientIp)) {
    return json({ error: 'Rate limit exceeded', retryAfter: 60 }, 429)
  }

  // Tool invocation — POST /invoke
  if (url.pathname === '/invoke' && req.method === 'POST') {
    let body: { tool: string; params: Record<string, unknown> }

    try {
      body = await req.json()
    } catch {
      return json({ error: 'Invalid JSON body' }, 400)
    }

    const { tool, params = {} } = body

    if (!tool || typeof tool !== 'string') {
      return json({ error: 'Missing "tool" field in request body' }, 400)
    }

    switch (tool) {
${toolCases}

      default:
        return json({
          error: \`Unknown tool: \${tool}\`,
          available: ${JSON.stringify(config.tools.map(t => t.name))},
        }, 404)
    }
  }

  // List tools — GET /tools
  if (url.pathname === '/tools' && req.method === 'GET') {
    return json({
      mcpVersion: '1.0',
      server: '${config.serverName}',
      tools: ${JSON.stringify(
    config.tools.map(t => ({
      name: t.name,
      description: t.description,
      inputSchema: t.input_schema,
    })),
    null,
    2,
  ).split('\n').map((line, i) => i === 0 ? line : `      ${line}`).join('\n')},
    })
  }

  return json({ error: 'Not found', endpoints: ['/health', '/invoke', '/tools'] }, 404)
})
`
}

// ─── Main Generator ───

export function generateMCPServer(config: MCPServerConfig): MCPDeploymentPreview {
  const slug = toSlug(config.serverName)
  const serverUrl = `https://<project-ref>.supabase.co/functions/v1/${slug}`
  const generatedCode = generateServerCode(config)
  const envVars = extractEnvVarsFromTools(config.tools)

  // Security notes
  const securityNotes: string[] = []

  for (const tool of config.tools) {
    if (hasCredentialInUrl(tool)) {
      securityNotes.push(`[${tool.name}] Credentials detected in URL — move to environment variables`)
    }

    if (tool.requires_auth && !tool.metadata?.auth_type) {
      securityNotes.push(`[${tool.name}] requires_auth is true but no auth_type specified — defaulting to bearer`)
    }

    if (tool.execution_mode === 'live' && !tool.requires_auth) {
      securityNotes.push(`[${tool.name}] Live execution mode without authentication — consider enabling auth`)
    }
  }

  if (config.corsOrigins.includes('*')) {
    securityNotes.push('CORS is set to allow all origins (*) — restrict in production')
  }

  if (config.rateLimitPerMinute > 120) {
    securityNotes.push(`Rate limit is high (${config.rateLimitPerMinute}/min) — consider lowering for production`)
  }

  // Tool endpoints
  const toolEndpoints = config.tools.map(tool => ({
    name: tool.name,
    method: 'POST',
    url: `${serverUrl}/invoke`,
  }))

  // Curl example using the first tool
  const firstTool = config.tools[0]

  const exampleParams = firstTool
    ? buildExampleParams(firstTool)
    : '{}'

  const curlExample = firstTool
    ? `curl -X POST ${serverUrl}/invoke \\
  -H 'Content-Type: application/json' \\
  -d '${JSON.stringify({ tool: firstTool.name, params: JSON.parse(exampleParams) })}'`
    : `curl ${serverUrl}/health`

  // MCP config
  const mcpConfig = generateMCPConfig(config.tools, config.serverName)

  const connectionInfo: MCPConnectionInfo = {
    serverUrl,
    serverSlug: slug,
    mcpConfig,
    curlExample,
    deployCommand: `supabase functions deploy ${slug} --no-verify-jwt`,
    envVars,
    toolEndpoints,
  }

  return {
    serverName: config.serverName,
    generatedCode,
    connectionInfo,
    toolCount: config.tools.length,
    securityNotes,
  }
}

// ─── Example Params Builder ───

function buildExampleParams(tool: ToolDefinition): string {
  const schema = tool.input_schema
  const properties = (schema.properties ?? {}) as Record<string, Record<string, unknown>>
  const required = extractRequiredParams(schema)
  const example: Record<string, unknown> = {}

  const keysToInclude = required.length > 0
    ? required
    : Object.keys(properties).slice(0, 3)

  for (const key of keysToInclude) {
    const prop = properties[key]

    if (!prop) {
      example[key] = 'value'
      continue
    }

    switch (prop.type) {
      case 'string':
        example[key] = (prop.example as string) ?? (prop.default as string) ?? 'example'
        break
      case 'number':
      case 'integer':
        example[key] = (prop.example as number) ?? (prop.default as number) ?? 1
        break
      case 'boolean':
        example[key] = (prop.example as boolean) ?? (prop.default as boolean) ?? true
        break
      case 'array':
        example[key] = (prop.example as unknown[]) ?? []
        break
      case 'object':
        example[key] = (prop.example as Record<string, unknown>) ?? {}
        break
      default:
        example[key] = 'value'
    }
  }

  return JSON.stringify(example)
}
