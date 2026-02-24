import type { SVGAttributes } from 'react'

const OrionLogo = (props: SVGAttributes<SVGElement>) => {
  return (
    <svg xmlns='http://www.w3.org/2000/svg' width='1em' height='1em' viewBox='0 0 32 32' fill='none' {...props}>
      <rect width='32' height='32' rx='16' transform='matrix(1 0 0 -1 0 32)' fill='var(--primary)' />
      <path
        d='M10.1758 6.00391L16.1782 9.47507L22.179 6.00391V9.68898L16.1782 13.1601L10.1758 9.68898V6.00391Z'
        fill='var(--primary-foreground)'
      />
      <path
        d='M6.57812 21.5853L10.0493 15.5828L6.57812 9.58203H10.2616L13.7344 15.5828L10.2616 21.5853H6.57812Z'
        fill='var(--primary-foreground)'
      />
      <path
        d='M22.179 25.1631L16.1782 21.6919L10.1758 25.1631V21.4796L16.1782 18.0068L22.179 21.4796V25.1631Z'
        fill='var(--primary-foreground)'
      />
      <path
        d='M25.7773 9.58203L22.3062 15.5828L25.7773 21.5853H22.0923L18.6211 15.5828L22.0923 9.58203H25.7773Z'
        fill='var(--primary-foreground)'
      />
    </svg>
  )
}

export default OrionLogo
