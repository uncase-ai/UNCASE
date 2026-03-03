import { redirect } from 'next/navigation'

/**
 * Legacy route — redirect to /sandbox which lives outside the
 * DashboardShell layout so the Topbar health check doesn't fire
 * before the sandbox session is established.
 */
export default function LegacySandboxPage({
  searchParams
}: {
  searchParams: Record<string, string>
}) {
  const params = new URLSearchParams(searchParams).toString()

  redirect(`/sandbox${params ? `?${params}` : ''}`)
}
