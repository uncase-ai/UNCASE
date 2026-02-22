/**
 * Extracts headings from MDX content string
 * @param content - The MDX content string
 * @returns Array of heading objects with slug, text, and depth
 */
export function extractHeadings(content: string): { slug: string; text: string; depth: number }[] {
  const headings: { slug: string; text: string; depth: number }[] = []

  // Regex to match markdown headings (## Heading, ### Heading, etc.)
  const headingRegex = /^(#{2,6})\s+(.+)$/gm

  let match

  while ((match = headingRegex.exec(content)) !== null) {
    const depth = match[1].length - 2 // Convert to 0-based depth (h2 = 0, h3 = 1, etc.)
    const text = match[2].trim()
    const slug = generateSlug(text)

    headings.push({ slug, text, depth })
  }

  return headings
}

/**
 * Generates a URL-friendly slug from text
 * @param text - The text to convert to a slug
 * @returns URL-friendly slug
 */
export function generateSlug(text: string): string {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-')
}
