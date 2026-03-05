import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_APP_URL ?? 'https://app.uncase.md'
  const now = new Date().toISOString()

  const publicRoutes: MetadataRoute.Sitemap = [
    {
      url: base,
      lastModified: now,
      changeFrequency: 'weekly',
      priority: 1.0
    },
    {
      url: `${base}/login`,
      lastModified: now,
      changeFrequency: 'monthly',
      priority: 0.3
    },
    {
      url: `${base}/register`,
      lastModified: now,
      changeFrequency: 'monthly',
      priority: 0.3
    }
  ]

  const dashboardRoutes = [
    { path: '/dashboard', priority: 0.8 },
    { path: '/dashboard/pipeline', priority: 0.7 },
    { path: '/dashboard/pipeline/seeds', priority: 0.7 },
    { path: '/dashboard/pipeline/seeds/new', priority: 0.6 },
    { path: '/dashboard/pipeline/seeds/extract', priority: 0.6 },
    { path: '/dashboard/pipeline/generate', priority: 0.7 },
    { path: '/dashboard/pipeline/evaluate', priority: 0.6 },
    { path: '/dashboard/pipeline/import', priority: 0.5 },
    { path: '/dashboard/pipeline/export', priority: 0.5 },
    { path: '/dashboard/pipeline/scenarios', priority: 0.5 },
    { path: '/dashboard/conversations', priority: 0.6 },
    { path: '/dashboard/evaluations', priority: 0.6 },
    { path: '/dashboard/templates', priority: 0.5 },
    { path: '/dashboard/tools', priority: 0.5 },
    { path: '/dashboard/knowledge', priority: 0.5 },
    { path: '/dashboard/plugins', priority: 0.5 },
    { path: '/dashboard/blockchain', priority: 0.5 },
    { path: '/dashboard/connectors', priority: 0.4 },
    { path: '/dashboard/costs', priority: 0.4 },
    { path: '/dashboard/jobs', priority: 0.4 },
    { path: '/dashboard/activity', priority: 0.4 },
    { path: '/dashboard/settings', priority: 0.3 },
    { path: '/dashboard/sandbox', priority: 0.3 }
  ]

  const dashboardSitemap: MetadataRoute.Sitemap = dashboardRoutes.map(route => ({
    url: `${base}${route.path}`,
    lastModified: now,
    changeFrequency: 'daily' as const,
    priority: route.priority
  }))

  return [...publicRoutes, ...dashboardSitemap]
}
