import { cn } from '@/lib/utils'

interface IconProps {
  name: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  filled?: boolean
  className?: string
}

const sizeMap = {
  sm: 'text-base',
  md: 'text-xl',
  lg: 'text-2xl',
  xl: 'text-3xl',
}

export function Icon({ name, size = 'md', filled = false, className }: IconProps) {
  return (
    <span
      className={cn(
        'material-symbols-outlined select-none',
        filled && 'filled',
        sizeMap[size],
        className
      )}
      aria-hidden="true"
    >
      {name}
    </span>
  )
}
