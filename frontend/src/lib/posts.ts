import fs from 'fs' // Comment this line if using remote fetching
import path from 'path' // Comment this line if using remote fetching

import matter from 'gray-matter'

export type Post = {
  metadata: PostMetadata
  content: string
}

export type PostMetadata = {
  slug: string
  title?: string
  description?: string
  category?: string
  publishedAt?: string
  author?: {
    name: string
    picture: string
  }
  image?: string
  featured?: boolean
  readTime?: string
  keywords?: string[]
}

// local content directory (comment below line if using remote fetching)
const rootDirectory = path.join(process.cwd(), 'src', 'content', 'blog')

// Remote repository details
// const GITHUB_USERNAME = 'yourusername'
// const GITHUB_REPO = 'reponame'
// const GITHUB_BRANCH = 'main'
// const CONTENT_PATH = 'content/blog'

export async function getPostBySlug(slug: string): Promise<Post | null> {
  try {
    // LOCAL LOGIC:
    const filePath = path.join(rootDirectory, `${slug}.mdx`)
    const fileContent = fs.readFileSync(filePath, { encoding: 'utf8' })

    // REMOTE LOGIC (commented for reference):
    // const res = await fetch(
    //   `https://raw.githubusercontent.com/${GITHUB_USERNAME}/${GITHUB_REPO}/refs/heads/${GITHUB_BRANCH}/${CONTENT_PATH}/${slug}.mdx`
    // )
    // const fileContent = await res.text()

    const { data, content } = matter(fileContent)

    return { metadata: { ...data, slug }, content }
  } catch {
    return null
  }
}

export async function getPosts(limit?: number): Promise<PostMetadata[]> {
  try {
    // LOCAL LOGIC:
    const files = fs.readdirSync(rootDirectory)
    const posts = await Promise.all(files.map(async (file: any) => await getPostMetadata(file)))

    // REMOTE LOGIC (commented for reference):
    // const res = await fetch(`https://api.github.com/repos/${GITHUB_USERNAME}/${GITHUB_REPO}/contents/${CONTENT_PATH}`)
    // const files = await res.json()
    // // Filter only .mdx files
    // const mdxFiles = files.filter((file: any) => file.name.endsWith('.mdx'))
    // // Fetch metadata for each file
    // const posts = await Promise.all(mdxFiles.map(async (file: any) => await getPostMetadata(file.name)))

    // Sort posts by published date
    const sortedPosts = posts.sort((a, b) => {
      if (new Date(a.publishedAt ?? '') < new Date(b.publishedAt ?? '')) {
        return 1
      } else {
        return -1
      }
    })

    if (limit) {
      return sortedPosts.slice(0, limit)
    }

    return sortedPosts
  } catch (error) {
    console.error('Error fetching posts:', error)

    return []
  }
}

export async function getPostMetadata(filepath: string): Promise<PostMetadata> {
  try {
    const slug = filepath.replace(/\.mdx$/, '')

    // LOCAL LOGIC:
    const filePath = path.join(rootDirectory, filepath)
    const fileContent = fs.readFileSync(filePath, { encoding: 'utf8' })

    // REMOTE LOGIC (commented for reference):
    // const res = await fetch(
    //   `https://raw.githubusercontent.com/${GITHUB_USERNAME}/${GITHUB_REPO}/refs/heads/${GITHUB_BRANCH}/${CONTENT_PATH}/${filepath}`
    // )
    // const fileContent = await res.text()

    const { data } = matter(fileContent)

    return { ...data, slug }
  } catch (error) {
    console.error(`Error fetching metadata for ${filepath}:`, error)

    return { slug: filepath.replace(/\.mdx$/, '') }
  }
}
