"use client";

import { useRef, useEffect, useState, type FormEvent, type KeyboardEvent } from "react";
import { useChat } from "@/hooks/useChat";
import { ChatMessage } from "./ChatMessage";
import { Button } from "@/components/ui/Button";

export function ChatWindow() {
  const { messages, isStreaming, error, sendMessage, stopStreaming } = useChat();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input.trim());
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  };

  return (
    <div className="flex h-full flex-col">
      {/* Messages area */}
      <div
        className="flex-1 overflow-y-auto px-4 py-6"
        role="list"
        aria-label="Chat messages"
        aria-live="polite"
      >
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-[var(--color-foreground)]">
                Travel AI Assistant
              </h2>
              <p className="mt-2 text-[var(--color-muted)]">
                Ask me about flights, hotels, itineraries, or travel tips.
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error display */}
      {error && (
        <div
          className="mx-4 mb-2 rounded-lg bg-[var(--color-error)]/10 px-4 py-2 text-sm text-[var(--color-error)]"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Input area */}
      <div className="border-t border-[var(--color-border)] px-4 py-3">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex max-w-3xl items-end gap-2"
        >
          <div className="flex-1">
            <label htmlFor="chat-input" className="sr-only">
              Type your message
            </label>
            <textarea
              ref={textareaRef}
              id="chat-input"
              rows={1}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Ask me about your travel plans..."
              className="w-full resize-none rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] px-4 py-2.5 text-sm focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/30"
              disabled={isStreaming}
              aria-label="Chat message input"
            />
          </div>

          {isStreaming ? (
            <Button
              type="button"
              variant="danger"
              size="md"
              onClick={stopStreaming}
              aria-label="Stop generating response"
            >
              Stop
            </Button>
          ) : (
            <Button
              type="submit"
              disabled={!input.trim()}
              size="md"
              aria-label="Send message"
            >
              Send
            </Button>
          )}
        </form>
      </div>
    </div>
  );
}
