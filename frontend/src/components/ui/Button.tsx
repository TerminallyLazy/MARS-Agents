import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius-md)] text-sm font-medium transition-all duration-[var(--transition-fast)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary:
          'bg-[var(--accent-primary)] text-white shadow-[0_2px_4px_rgba(124,92,255,0.2)] hover:bg-[var(--accent-deep)] hover:shadow-[0_4px_8px_rgba(124,92,255,0.3)] hover:-translate-y-px',
        secondary:
          'bg-[var(--bg-secondary)] text-[var(--text-default)] border border-[var(--border-default)] shadow-[var(--shadow-sm)] hover:bg-[var(--bg-tertiary)] hover:border-[var(--border-strong)]',
        ghost:
          'bg-transparent text-[var(--text-muted)] hover:bg-[var(--overlay-light)] hover:text-[var(--text-default)]',
        destructive:
          'bg-[var(--color-error)] text-white hover:bg-[var(--color-error)]/90',
        outline:
          'border-[1.5px] border-dashed border-[var(--border-dashed)] bg-transparent text-[var(--text-default)] hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)] hover:bg-[var(--accent-light)]',
        link: 'text-[var(--accent-primary)] underline-offset-4 hover:underline',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-9 px-4',
        lg: 'h-10 px-6',
        xl: 'h-11 px-8 text-base',
        icon: 'h-9 w-9',
        'icon-sm': 'h-8 w-8',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)

Button.displayName = 'Button'
