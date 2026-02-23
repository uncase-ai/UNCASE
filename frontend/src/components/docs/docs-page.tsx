'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import {
  Search,
  ChevronRight,
  ChevronDown,
  Menu,
  ArrowLeft,
  FileText,
  Home,
  Languages,
} from 'lucide-react'
import Link from 'next/link'

import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { cn } from '@/lib/utils'
import { CATEGORIES, ARTICLES, type DocArticle, type DocCategory, type Locale } from '@/assets/data/docs'

// ── Helpers ─────────────────────────────────────────────────

function t(obj: { en: string; es: string }, locale: Locale): string {
  return obj[locale]
}

function groupByCategory(articles: DocArticle[]): Record<string, DocArticle[]> {
  const grouped: Record<string, DocArticle[]> = {}
  for (const article of articles) {
    if (!grouped[article.category]) grouped[article.category] = []
    grouped[article.category].push(article)
  }
  for (const key of Object.keys(grouped)) {
    grouped[key].sort((a, b) => a.order - b.order)
  }
  return grouped
}

const CONTENT_CLASSES = cn(
  '[&_h2]:text-xl [&_h2]:font-semibold [&_h2]:mt-8 [&_h2]:mb-3 [&_h2]:text-foreground',
  '[&_h3]:text-lg [&_h3]:font-medium [&_h3]:mt-6 [&_h3]:mb-2 [&_h3]:text-foreground',
  '[&_p]:mb-4 [&_p]:leading-relaxed [&_p]:text-muted-foreground',
  '[&_ul]:list-disc [&_ul]:pl-6 [&_ul]:mb-4 [&_ul]:text-muted-foreground',
  '[&_ol]:list-decimal [&_ol]:pl-6 [&_ol]:mb-4 [&_ol]:text-muted-foreground',
  '[&_li]:mb-1.5',
  '[&_strong]:text-foreground [&_strong]:font-semibold',
  '[&_code]:bg-muted [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-sm [&_code]:font-mono',
  '[&_pre]:bg-muted [&_pre]:p-4 [&_pre]:rounded-lg [&_pre]:overflow-x-auto [&_pre]:mb-4 [&_pre]:text-sm',
  '[&_pre_code]:bg-transparent [&_pre_code]:p-0',
  '[&_a]:text-foreground [&_a]:underline [&_a]:underline-offset-4',
  '[&_table]:w-full [&_table]:mb-4 [&_table]:text-sm',
  '[&_thead]:border-b [&_thead]:border-border',
  '[&_th]:text-left [&_th]:p-2.5 [&_th]:font-medium [&_th]:text-foreground',
  '[&_td]:p-2.5 [&_td]:text-muted-foreground [&_td]:border-b [&_td]:border-border/50',
  '[&_hr]:my-6 [&_hr]:border-border',
)

// ── Sidebar Component ───────────────────────────────────────

type SidebarProps = {
  locale: Locale
  groupedArticles: Record<string, DocArticle[]>
  selectedArticleId: string | null
  selectedCategory: string | null
  searchQuery: string
  openCategories: Set<string>
  onSearchChange: (q: string) => void
  onSelectArticle: (id: string) => void
  onSelectCategory: (cat: string) => void
  onToggleCategory: (cat: string) => void
  onGoHome: () => void
}

function DocsSidebar({
  locale,
  groupedArticles,
  selectedArticleId,
  selectedCategory,
  searchQuery,
  openCategories,
  onSearchChange,
  onSelectArticle,
  onSelectCategory,
  onToggleCategory,
  onGoHome,
}: SidebarProps) {
  const sortedCategories = useMemo(
    () => [...CATEGORIES].sort((a, b) => a.order - b.order),
    [],
  )

  return (
    <div className="flex h-full flex-col">
      {/* Home button */}
      <button
        onClick={onGoHome}
        className={cn(
          'flex items-center gap-2 px-3 py-2.5 text-sm font-medium transition-colors',
          'hover:bg-accent rounded-lg',
          !selectedCategory && !selectedArticleId ? 'text-foreground' : 'text-muted-foreground',
        )}
      >
        <Home className="size-4" />
        {locale === 'en' ? 'Documentation' : 'Documentación'}
      </button>

      <Separator className="my-2" />

      {/* Search */}
      <div className="relative px-1 pb-3">
        <Search className="text-muted-foreground absolute top-2.5 left-3.5 size-4" />
        <Input
          placeholder={locale === 'en' ? 'Search docs...' : 'Buscar docs...'}
          value={searchQuery}
          onChange={e => onSearchChange(e.target.value)}
          className="h-9 pl-9 text-sm"
        />
      </div>

      {/* Category tree */}
      <div className="flex-1 overflow-y-auto px-1">
        {sortedCategories.map(cat => {
          const articles = groupedArticles[cat.id] || []
          if (articles.length === 0 && searchQuery) return null
          const isOpen = openCategories.has(cat.id)
          const Icon = cat.icon

          return (
            <Collapsible key={cat.id} open={isOpen} onOpenChange={() => onToggleCategory(cat.id)}>
              <CollapsibleTrigger asChild>
                <button
                  className={cn(
                    'flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors',
                    'hover:bg-accent',
                    selectedCategory === cat.id && !selectedArticleId
                      ? 'bg-accent text-foreground font-medium'
                      : 'text-muted-foreground',
                  )}
                >
                  <span className="flex items-center gap-2">
                    <Icon className="size-4" />
                    {t(cat.label, locale)}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="text-muted-foreground/60 text-xs">{articles.length}</span>
                    {isOpen ? <ChevronDown className="size-3.5" /> : <ChevronRight className="size-3.5" />}
                  </span>
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <div className="ml-4 border-l border-border/50 pl-2 py-1">
                  {/* Category overview link */}
                  <button
                    onClick={() => onSelectCategory(cat.id)}
                    className={cn(
                      'flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-xs transition-colors',
                      'hover:bg-accent',
                      selectedCategory === cat.id && !selectedArticleId
                        ? 'text-foreground font-medium'
                        : 'text-muted-foreground',
                    )}
                  >
                    {locale === 'en' ? 'Overview' : 'Resumen'}
                  </button>
                  {/* Article links */}
                  {articles.map(article => (
                    <button
                      key={article.id}
                      onClick={() => onSelectArticle(article.id)}
                      className={cn(
                        'flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-xs transition-colors',
                        'hover:bg-accent',
                        selectedArticleId === article.id
                          ? 'text-foreground font-medium'
                          : 'text-muted-foreground',
                      )}
                    >
                      {t(article.title, locale)}
                    </button>
                  ))}
                </div>
              </CollapsibleContent>
            </Collapsible>
          )
        })}
      </div>
    </div>
  )
}

// ── Category Cards View ─────────────────────────────────────

function CategoryCardsView({
  locale,
  groupedArticles,
  onSelectCategory,
}: {
  locale: Locale
  groupedArticles: Record<string, DocArticle[]>
  onSelectCategory: (cat: string) => void
}) {
  const sortedCategories = useMemo(
    () => [...CATEGORIES].sort((a, b) => a.order - b.order),
    [],
  )

  return (
    <div>
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
        {locale === 'en' ? 'Documentation' : 'Documentación'}
      </h1>
      <p className="text-muted-foreground mt-2 text-base">
        {locale === 'en'
          ? 'Guides, references, and resources for the UNCASE framework.'
          : 'Guías, referencias y recursos para el framework UNCASE.'}
      </p>

      <div className="mt-8 grid gap-3 sm:grid-cols-2">
        {sortedCategories.map(cat => {
          const articles = groupedArticles[cat.id] || []
          const Icon = cat.icon
          return (
            <button
              key={cat.id}
              onClick={() => onSelectCategory(cat.id)}
              className={cn(
                'group flex items-start gap-4 rounded-xl border border-border/60 p-4 text-left transition-all',
                'hover:border-border hover:bg-accent/40',
              )}
            >
              <div className="bg-muted flex size-10 shrink-0 items-center justify-center rounded-lg">
                <Icon className="text-muted-foreground size-5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-foreground text-sm font-medium">{t(cat.label, locale)}</span>
                  <ChevronRight className="text-muted-foreground/50 size-4 transition-transform group-hover:translate-x-0.5" />
                </div>
                <p className="text-muted-foreground mt-0.5 text-xs leading-relaxed">{t(cat.description, locale)}</p>
                <span className="text-muted-foreground/60 mt-2 inline-block text-xs">
                  {articles.length} {locale === 'en' ? (articles.length === 1 ? 'article' : 'articles') : (articles.length === 1 ? 'artículo' : 'artículos')}
                </span>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}

// ── Category View ───────────────────────────────────────────

function CategoryView({
  locale,
  category,
  articles,
  onSelectArticle,
  onGoHome,
}: {
  locale: Locale
  category: DocCategory
  articles: DocArticle[]
  onSelectArticle: (id: string) => void
  onGoHome: () => void
}) {
  const Icon = category.icon

  return (
    <div>
      <button
        onClick={onGoHome}
        className="text-muted-foreground hover:text-foreground mb-6 flex items-center gap-1.5 text-sm transition-colors"
      >
        <ArrowLeft className="size-4" />
        {locale === 'en' ? 'All categories' : 'Todas las categorías'}
      </button>

      <div className="mb-8 flex items-center gap-3">
        <div className="bg-muted flex size-10 items-center justify-center rounded-lg">
          <Icon className="text-muted-foreground size-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t(category.label, locale)}</h1>
          <p className="text-muted-foreground text-sm">{t(category.description, locale)}</p>
        </div>
      </div>

      <div className="space-y-1.5">
        {articles.map(article => (
          <button
            key={article.id}
            onClick={() => onSelectArticle(article.id)}
            className={cn(
              'group flex w-full items-center gap-3 rounded-lg border border-transparent p-3 text-left transition-all',
              'hover:border-border/60 hover:bg-accent/40',
            )}
          >
            <FileText className="text-muted-foreground/60 size-4 shrink-0" />
            <div className="min-w-0 flex-1">
              <span className="text-foreground text-sm font-medium">{t(article.title, locale)}</span>
              <p className="text-muted-foreground mt-0.5 truncate text-xs">{t(article.description, locale)}</p>
            </div>
            <ChevronRight className="text-muted-foreground/40 size-4 shrink-0 transition-transform group-hover:translate-x-0.5" />
          </button>
        ))}
      </div>
    </div>
  )
}

// ── Article View ────────────────────────────────────────────

function ArticleView({
  locale,
  article,
  category,
  onBack,
}: {
  locale: Locale
  article: DocArticle
  category: DocCategory
  onBack: () => void
}) {
  return (
    <div>
      <button
        onClick={onBack}
        className="text-muted-foreground hover:text-foreground mb-6 flex items-center gap-1.5 text-sm transition-colors"
      >
        <ArrowLeft className="size-4" />
        {t(category.label, locale)}
      </button>

      <Badge variant="secondary" className="mb-3 text-xs font-normal">
        {t(category.label, locale)}
      </Badge>
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{t(article.title, locale)}</h1>
      <p className="text-muted-foreground mt-1 text-sm">
        {locale === 'en' ? 'Last updated' : 'Última actualización'}: {article.lastUpdated}
      </p>

      <Separator className="my-6" />

      <div className={CONTENT_CLASSES} dangerouslySetInnerHTML={{ __html: t(article.content, locale) }} />

      {article.keywords.length > 0 && (
        <>
          <Separator className="my-6" />
          <div className="flex flex-wrap gap-1.5">
            {article.keywords.map(kw => (
              <Badge key={kw} variant="outline" className="text-muted-foreground text-xs font-normal">
                {kw}
              </Badge>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// ── Main Component ──────────────────────────────────────────

export default function DocsPage() {
  const [locale, setLocale] = useState<Locale>('en')
  const [selectedArticleId, setSelectedArticleId] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const [openCategories, setOpenCategories] = useState<Set<string>>(() => new Set(CATEGORIES.map(c => c.id)))

  // Hash routing
  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.slice(1)
      if (hash.startsWith('cat-')) {
        const catId = hash.replace('cat-', '')
        setSelectedCategory(catId)
        setSelectedArticleId(null)
      } else if (hash) {
        const article = ARTICLES.find(a => a.id === hash)
        if (article) {
          setSelectedArticleId(hash)
          setSelectedCategory(article.category)
          setOpenCategories(prev => new Set([...prev, article.category]))
        }
      } else {
        setSelectedArticleId(null)
        setSelectedCategory(null)
      }
    }
    handleHash()
    window.addEventListener('popstate', handleHash)
    return () => window.removeEventListener('popstate', handleHash)
  }, [])

  // Filter articles by search
  const filteredArticles = useMemo(() => {
    if (!searchQuery.trim()) return ARTICLES
    const q = searchQuery.toLowerCase()
    return ARTICLES.filter(
      a =>
        t(a.title, locale).toLowerCase().includes(q) ||
        t(a.description, locale).toLowerCase().includes(q) ||
        a.keywords.some(k => k.toLowerCase().includes(q)),
    )
  }, [searchQuery, locale])

  const groupedArticles = useMemo(() => groupByCategory(filteredArticles), [filteredArticles])

  // Navigation handlers
  const navigate = useCallback((hash: string) => {
    window.history.pushState(null, '', hash || window.location.pathname)
    window.dispatchEvent(new PopStateEvent('popstate'))
  }, [])

  const handleSelectArticle = useCallback(
    (id: string) => {
      navigate(`#${id}`)
      setMobileOpen(false)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    [navigate],
  )

  const handleSelectCategory = useCallback(
    (cat: string) => {
      navigate(`#cat-${cat}`)
      setMobileOpen(false)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    [navigate],
  )

  const handleGoHome = useCallback(() => {
    navigate('')
    setMobileOpen(false)
  }, [navigate])

  const handleToggleCategory = useCallback((cat: string) => {
    setOpenCategories(prev => {
      const next = new Set(prev)
      if (next.has(cat)) next.delete(cat)
      else next.add(cat)
      return next
    })
  }, [])

  // Current category/article
  const currentCategory = CATEGORIES.find(c => c.id === selectedCategory)
  const currentArticle = selectedArticleId ? ARTICLES.find(a => a.id === selectedArticleId) : null
  const currentCategoryArticles = selectedCategory ? (groupedArticles[selectedCategory] || []) : []

  // Sidebar props
  const sidebarProps: SidebarProps = {
    locale,
    groupedArticles,
    selectedArticleId,
    selectedCategory,
    searchQuery,
    openCategories,
    onSearchChange: setSearchQuery,
    onSelectArticle: handleSelectArticle,
    onSelectCategory: handleSelectCategory,
    onToggleCategory: handleToggleCategory,
    onGoHome: handleGoHome,
  }

  return (
    <div className="min-h-[80vh]">
      {/* ── Breadcrumb Bar ─────────────────────────────────── */}
      <div className="bg-background/95 sticky top-0 z-10 border-b backdrop-blur-sm">
        <div className="flex items-center gap-3 px-4 py-3 sm:px-6">
          {/* Mobile menu trigger */}
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon-sm" className="lg:hidden">
                <Menu className="size-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80 p-4">
              <ScrollArea className="h-full">
                <DocsSidebar {...sidebarProps} />
              </ScrollArea>
            </SheetContent>
          </Sheet>

          {/* Breadcrumb */}
          <Breadcrumb className="flex-1">
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link href="/">Home</Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <button onClick={handleGoHome} className="hover:text-foreground transition-colors">
                    Docs
                  </button>
                </BreadcrumbLink>
              </BreadcrumbItem>
              {currentCategory && (
                <>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbLink asChild>
                      <button
                        onClick={() => handleSelectCategory(currentCategory.id)}
                        className="hover:text-foreground transition-colors"
                      >
                        {t(currentCategory.label, locale)}
                      </button>
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                </>
              )}
              {currentArticle && (
                <>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <span className="text-foreground text-sm font-medium">
                      {t(currentArticle.title, locale)}
                    </span>
                  </BreadcrumbItem>
                </>
              )}
            </BreadcrumbList>
          </Breadcrumb>

          {/* Language toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setLocale(prev => (prev === 'en' ? 'es' : 'en'))}
            className="text-muted-foreground hover:text-foreground gap-1.5 text-xs"
          >
            <Languages className="size-3.5" />
            {locale === 'en' ? 'ES' : 'EN'}
          </Button>
        </div>
      </div>

      {/* ── Content Area ──────────────────────────────────── */}
      <div className="flex gap-0 lg:gap-0">
        {/* Desktop sidebar */}
        <aside className="hidden lg:block w-64 shrink-0 border-r">
          <div className="sticky top-12 max-h-[calc(100dvh-3rem)] overflow-y-auto p-4">
            <DocsSidebar {...sidebarProps} />
          </div>
        </aside>

        {/* Main content */}
        <main className="min-w-0 flex-1 px-4 py-8 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-3xl">
            {currentArticle && currentCategory ? (
              <ArticleView
                locale={locale}
                article={currentArticle}
                category={currentCategory}
                onBack={() => handleSelectCategory(currentCategory.id)}
              />
            ) : currentCategory ? (
              <CategoryView
                locale={locale}
                category={currentCategory}
                articles={currentCategoryArticles}
                onSelectArticle={handleSelectArticle}
                onGoHome={handleGoHome}
              />
            ) : (
              <CategoryCardsView
                locale={locale}
                groupedArticles={groupedArticles}
                onSelectCategory={handleSelectCategory}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
