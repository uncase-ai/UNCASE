import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000'
  const routes = ['/dashboard', '/login', '/register']

  return routes.map(route => ({
    url: `${base}${route}`
  }))
}
