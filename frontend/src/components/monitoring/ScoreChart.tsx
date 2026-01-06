import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'

interface ScoreChartProps {
  scores: number[]
  targetScore?: number
  className?: string
}

export function ScoreChart({
  scores,
  targetScore = 8.5,
  className,
}: ScoreChartProps) {
  if (scores.length === 0) {
    return (
      <div className={cn('p-4', className)}>
        <p className="text-sm text-[var(--text-muted)]">No scores yet</p>
      </div>
    )
  }

  const maxScore = 10
  const minDisplayScore = 0
  const chartHeight = 80
  const chartWidth = Math.max(scores.length * 40, 200)

  const getY = (score: number) => {
    const ratio = (score - minDisplayScore) / (maxScore - minDisplayScore)
    return chartHeight - ratio * chartHeight
  }

  const targetY = getY(targetScore)
  const currentScore = scores[scores.length - 1]
  const previousScore = scores.length > 1 ? scores[scores.length - 2] : null
  const delta = previousScore ? currentScore - previousScore : null

  const pathData = scores
    .map((score, i) => {
      const x = (i / (scores.length - 1 || 1)) * chartWidth
      const y = getY(score)
      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
    })
    .join(' ')

  return (
    <div className={cn('p-4 space-y-3', className)}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-[var(--text-default)]">
          Score Progression
        </span>
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-[var(--text-loud)]">
            {currentScore.toFixed(1)}
          </span>
          {delta !== null && (
            <span
              className={cn(
                'flex items-center gap-0.5 text-sm font-medium',
                delta >= 0 ? 'text-[var(--color-success)]' : 'text-[var(--color-error)]'
              )}
            >
              <Icon name={delta >= 0 ? 'trending_up' : 'trending_down'} size="sm" />
              {delta >= 0 ? '+' : ''}{delta.toFixed(1)}
            </span>
          )}
        </div>
      </div>

      <svg
        viewBox={`0 0 ${chartWidth} ${chartHeight + 20}`}
        className="w-full h-auto"
        preserveAspectRatio="xMidYMid meet"
      >
        <line
          x1="0"
          y1={targetY}
          x2={chartWidth}
          y2={targetY}
          stroke="var(--color-success)"
          strokeWidth="1"
          strokeDasharray="4 4"
          opacity="0.5"
        />
        <text
          x={chartWidth - 4}
          y={targetY - 4}
          fill="var(--color-success)"
          fontSize="10"
          textAnchor="end"
        >
          {targetScore}
        </text>

        <path
          d={pathData}
          fill="none"
          stroke="var(--accent-secondary)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {scores.map((score, i) => {
          const x = (i / (scores.length - 1 || 1)) * chartWidth
          const y = getY(score)
          const isLast = i === scores.length - 1
          return (
            <g key={i}>
              <circle
                cx={x}
                cy={y}
                r={isLast ? 5 : 3}
                fill={
                  score >= targetScore
                    ? 'var(--color-success)'
                    : 'var(--accent-secondary)'
                }
              />
              <text
                x={x}
                y={chartHeight + 14}
                fill="var(--text-muted)"
                fontSize="10"
                textAnchor="middle"
              >
                {i + 1}
              </text>
            </g>
          )
        })}
      </svg>

      <div className="flex items-center justify-center text-xs text-[var(--text-subtle)]">
        <span>Iteration</span>
      </div>
    </div>
  )
}
