import Link from 'next/link'

import { PrimaryFlowButton } from '@/components/ui/flow-button'

import Icon404 from '@/assets/svg/404'

const NotFound = () => {
  return (
    <div className='flex h-screen w-screen flex-col items-center justify-center gap-9 p-6'>
      <Icon404 className='h-auto w-full sm:h-120 sm:w-146' />
      <div className='flex flex-col items-center gap-4 text-center'>
        <p className='text-muted-foreground text-xl sm:text-2xl'>We couldn&apos;t find the page you are looking for</p>
        <PrimaryFlowButton size='lg' asChild>
          <Link href='/'>Go back to home</Link>
        </PrimaryFlowButton>
      </div>
    </div>
  )
}

export default NotFound
