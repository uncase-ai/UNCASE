import { redirect } from 'next/navigation'

/**
 * Legacy route — redirect to /sandbox which lives outside the
 * DashboardShell layout so the Topbar health check doesn't fire
 * before the sandbox session is established.
 */
export default async function LegacySandboxPage({ searchParams }: { searchParams: Promise<Record<string, string>> }) {
  const resolved = await searchParams
  const params = new URLSearchParams(resolved).toString()

  redirect(`/sandbox${params ? `?${params}` : ''}`)
}
