'use client'

import { ArrowRightIcon, GithubIcon, InstagramIcon, TwitterIcon, YoutubeIcon } from 'lucide-react'

import Link from 'next/link'

import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'

import Logo from '@/components/logo'
import { PrimaryFlowButton } from '@/components/ui/flow-button'
import SectionSeparator from '@/components/section-separator'

const Footer = () => {
  return (
    <footer>
      <SectionSeparator />
      <div className='mx-auto grid max-w-7xl grid-cols-6 gap-6 px-4 py-8 sm:gap-8 sm:px-6 sm:py-16 md:py-24 lg:px-8'>
        <div className='col-span-full flex flex-col items-start gap-4 lg:col-span-2'>
          <Link href='/#home'>
            <Logo />
          </Link>
          <p className='text-muted-foreground'>
            UNCASE — Open-source framework for turning sensitive conversations into trained AI models with zero PII
            exposure. LLM Gateway, Privacy Interceptor, and LoRA pipeline for regulated industries.
          </p>
          <Separator className='w-35!' />
          <div className='flex items-center gap-4'>
            <Link href='https://github.com/marianomoralesr/UNCASE' aria-label='Github Link'>
              <GithubIcon className='text-muted-foreground hover:text-foreground size-5' />
            </Link>
            <Link href='#' aria-label='Instagram Link'>
              <InstagramIcon className='text-muted-foreground hover:text-foreground size-5' />
            </Link>
            <Link href='#' aria-label='Twitter Link'>
              <TwitterIcon className='text-muted-foreground hover:text-foreground size-5' />
            </Link>
            <Link href='#' aria-label='Youtube Link'>
              <YoutubeIcon className='text-muted-foreground hover:text-foreground size-5' />
            </Link>
          </div>
        </div>
        <div className='col-span-full grid grid-cols-2 gap-6 sm:grid-cols-4 lg:col-span-4 lg:gap-8'>
          <div className='flex flex-col gap-5'>
            <div className='text-lg font-medium'>Framework</div>
            <ul className='text-muted-foreground space-y-3'>
              <li>
                <Link href='/#features' className='hover:text-foreground transition-colors duration-300'>
                  Architecture
                </Link>
              </li>
              <li>
                <Link href='/#benefits' className='hover:text-foreground transition-colors duration-300'>
                  Benefits
                </Link>
              </li>
              <li>
                <Link href='/#pipeline' className='hover:text-foreground transition-colors duration-300'>
                  Pipeline
                </Link>
              </li>
              <li>
                <Link href='/#capabilities' className='hover:text-foreground transition-colors duration-300'>
                  Capabilities
                </Link>
              </li>
              <li>
                <Link href='/#faq' className='hover:text-foreground transition-colors duration-300'>
                  FAQ
                </Link>
              </li>
            </ul>
          </div>
          <div className='flex flex-col gap-5'>
            <div className='text-lg font-medium'>Resources</div>
            <ul className='text-muted-foreground space-y-3'>
              <li>
                <Link href='https://github.com/marianomoralesr/UNCASE' className='hover:text-foreground transition-colors duration-300'>
                  GitHub Repository
                </Link>
              </li>
              <li>
                <Link href='https://github.com/marianomoralesr/UNCASE/issues' className='hover:text-foreground transition-colors duration-300'>
                  Report Issues
                </Link>
              </li>
              <li>
                <Link href='#' className='hover:text-foreground transition-colors duration-300'>
                  SCSF Whitepaper
                </Link>
              </li>
              <li>
                <Link href='#' className='hover:text-foreground transition-colors duration-300'>
                  Contributing Guide
                </Link>
              </li>
            </ul>
          </div>
          <div className='col-span-full flex flex-col gap-5 sm:col-span-2'>
            <div>
              <p className='mb-3 text-lg font-medium'>Subscribe to newsletter</p>
              <form className='flex gap-2' onSubmit={e => e.preventDefault()}>
                <Input name='newsletter-email' type='email' placeholder='Your email...' required />
                <PrimaryFlowButton size='icon' type='submit' className='shrink-0' aria-label='Newsletter submit button'>
                  <ArrowRightIcon />
                </PrimaryFlowButton>
              </form>
            </div>
            <Separator />

            <div className='flex flex-wrap justify-center gap-4'>
              <img src='/images/brand-logos/bestofjs-logo-bw.webp' alt='bestofjs' className='h-5 dark:invert' />
              <img src='/images/brand-logos/product-hunt-logo-bw.webp' alt='producthunt' className='h-5 dark:invert' />
              <img src='/images/brand-logos/reddit-logo-bw.webp' alt='reddit' className='h-5 dark:invert' />
              <img src='/images/brand-logos/medium-logo-bw.webp' alt='medium' className='h-5 dark:invert' />
              <img src='/images/brand-logos/ycombinator-logo-bw.webp' alt='ycombinator' className='h-5 dark:invert' />
              <img src='/images/brand-logos/launchtory-logo-bw.webp' alt='launchtory' className='h-5 dark:invert' />
            </div>
          </div>
        </div>
      </div>

      <Separator />

      <div className='mx-auto flex max-w-7xl justify-center px-4 py-6 sm:px-6'>
        <p className='text-muted-foreground text-center text-balance'>
          {`©2025–${new Date().getFullYear()}`}{' '}
          <Link className='text-foreground font-medium hover:underline' href='/#home'>
            UNCASE
          </Link>{' '}
          — Privacy-First AI Infrastructure for Regulated Industries.
        </p>
      </div>
    </footer>
  )
}

export default Footer
