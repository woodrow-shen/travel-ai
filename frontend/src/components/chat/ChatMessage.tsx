import type { ChatMessage as ChatMessageType } from "@/types";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full gap-3",
        isUser ? "justify-end" : "justify-start"
      )}
      role="listitem"
    >
      {/* Avatar */}
      {!isUser && (
        <div
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-sm font-medium text-white"
          aria-hidden="true"
        >
          AI
        </div>
      )}

      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-2.5",
          isUser
            ? "bg-[var(--color-primary)] text-white"
            : "bg-[var(--color-border)]/40 text-[var(--color-foreground)]"
        )}
      >
        <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
          {message.content}
          {!isUser && message.content === "" && (
            <span className="inline-flex gap-1" aria-label="Typing">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--color-muted)] [animation-delay:0ms]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--color-muted)] [animation-delay:150ms]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--color-muted)] [animation-delay:300ms]" />
            </span>
          )}
        </div>
        <time
          className={cn(
            "mt-1 block text-xs",
            isUser ? "text-white/70" : "text-[var(--color-muted)]"
          )}
          dateTime={message.timestamp}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </time>
      </div>

      {/* User avatar */}
      {isUser && (
        <div
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[var(--color-muted)] text-sm font-medium text-white"
          aria-hidden="true"
        >
          U
        </div>
      )}
    </div>
  );
}
