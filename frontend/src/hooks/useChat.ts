"use client";

import { useCallback, useRef } from "react";
import { api } from "@/lib/api";
import { useChatStore } from "@/stores/chat";

export function useChat() {
  const messages = useChatStore((s) => s.messages);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const error = useChatStore((s) => s.error);
  const tripId = useChatStore((s) => s.tripId);
  const addUserMessage = useChatStore((s) => s.addUserMessage);
  const startAssistantMessage = useChatStore((s) => s.startAssistantMessage);
  const appendToAssistantMessage = useChatStore((s) => s.appendToAssistantMessage);
  const finishStreaming = useChatStore((s) => s.finishStreaming);
  const setError = useChatStore((s) => s.setError);
  const setTripId = useChatStore((s) => s.setTripId);
  const clearMessages = useChatStore((s) => s.clearMessages);

  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    (content: string) => {
      if (isStreaming || !content.trim()) return;

      addUserMessage(content);
      const assistantId = startAssistantMessage();

      abortRef.current = api.streamSSE(
        "/chat",
        {
          message: content,
          trip_id: tripId,
        },
        (event) => {
          switch (event.type) {
            case "text":
              appendToAssistantMessage(assistantId, event.data);
              break;
            case "data":
              try {
                const parsed = JSON.parse(event.data);
                appendToAssistantMessage(
                  assistantId,
                  parsed.content ?? event.data
                );
              } catch {
                appendToAssistantMessage(assistantId, event.data);
              }
              break;
            case "done":
              finishStreaming();
              break;
            case "error":
              setError(event.data);
              break;
          }
        },
        (error) => {
          const message =
            error && typeof error === "object" && "detail" in error
              ? (error as { detail: string }).detail
              : "Chat connection failed. Please try again.";
          setError(message);
        },
        () => {
          finishStreaming();
        }
      );
    },
    [isStreaming, tripId, addUserMessage, startAssistantMessage, appendToAssistantMessage, finishStreaming, setError]
  );

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
    finishStreaming();
  }, [finishStreaming]);

  return {
    messages,
    isStreaming,
    error,
    tripId,
    sendMessage,
    stopStreaming,
    setTripId,
    clearMessages,
  };
}
