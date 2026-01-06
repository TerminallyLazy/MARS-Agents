import { cn } from '@/lib/utils'
import { Icon } from '@/components/ui/Icon'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { formatTimestamp } from '@/lib/utils'
import type { ChatMessage } from '@/stores/chatStore'

interface MessageBubbleProps {
  message: ChatMessage
  onViewDetails?: () => void
}

export function MessageBubble({ message, onViewDetails }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'

  const score = message.metadata?.score
  const previousScore = message.metadata?.previousScore
  const iteration = message.metadata?.iteration
  const isStreaming = message.metadata?.isStreaming

  const scoreDelta = score && previousScore ? score - previousScore : null
  const scorePercent = score ? (score / 10) * 100 : 0

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser && 'flex-row-reverse'
      )}
    >
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser
            ? 'bg-[var(--accent-secondary)]/20 text-[var(--accent-secondary)]'
            : 'bg-[var(--color-success)]/20 text-[var(--color-success)]'
        )}
      >
        <Icon name={isUser ? 'person' : 'smart_toy'} size="sm" />
      </div>

      <div
        className={cn(
          'flex-1 max-w-[80%] space-y-2',
          isUser && 'flex flex-col items-end'
        )}
      >
        <div className="flex items-center gap-2 text-sm">
          <span className="font-medium text-[var(--text-default)]">
            {isUser ? 'You' : 'MARS'}
          </span>
          {iteration && (
            <Badge variant="accent">Iteration {iteration}</Badge>
          )}
          <span className="text-[var(--text-subtle)]">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        <div
          className={cn(
            'rounded-[var(--radius-lg)] p-4',
            isUser
              ? 'bg-[var(--accent-primary)] text-white'
              : 'bg-[var(--bg-secondary)] border border-[var(--border-default)] text-[var(--text-default)]'
          )}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>

          {isAssistant && score !== undefined && (
            <div className="mt-4 pt-4 border-t border-[var(--border-default)] space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[var(--text-muted)]">Score</span>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-[var(--text-loud)]">
                    {score.toFixed(1)}/10
                  </span>
                  {scoreDelta !== null && (
                    <span
                      className={cn(
                        'text-sm font-medium flex items-center gap-0.5',
                        scoreDelta >= 0
                          ? 'text-[var(--color-success)]'
                          : 'text-[var(--color-error)]'
                      )}
                    >
                      <Icon
                        name={scoreDelta >= 0 ? 'trending_up' : 'trending_down'}
                        size="sm"
                      />
                      {scoreDelta >= 0 ? '+' : ''}
                      {scoreDelta.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>

              <div className="w-full h-2 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
                <div
                  className={cn(
                    'h-full rounded-full transition-all duration-500',
                    scorePercent >= 85
                      ? 'bg-[var(--color-success)]'
                      : scorePercent >= 70
                      ? 'bg-[var(--color-warning)]'
                      : 'bg-[var(--color-error)]'
                  )}
                  style={{ width: `${scorePercent}%` }}
                />
              </div>

              {onViewDetails && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onViewDetails}
                  className="mt-2"
                >
                  <Icon name="visibility" size="sm" />
                  View Details
                </Button>
              )}
            </div>
          )}

          {isStreaming && (
            <span className="inline-block ml-1 animate-pulse">
              <Icon name="more_horiz" size="sm" />
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
