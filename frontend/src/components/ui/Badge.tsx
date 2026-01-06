import { cn } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-[var(--overlay-light)] text-[var(--text-muted)]',
        success: 'bg-[var(--color-success)]/15 text-[var(--color-success)]',
        warning: 'bg-[var(--color-warning)]/15 text-[var(--color-warning)]',
        error: 'bg-[var(--color-error)]/15 text-[var(--color-error)]',
        info: 'bg-[var(--color-info)]/15 text-[var(--color-info)]',
        accent: 'bg-[var(--accent-secondary)]/15 text-[var(--accent-secondary)]',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}
