import { create } from "zustand";
import type { ChatMessage } from "@/types";
import { generateId } from "@/lib/utils";

interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  tripId: string | null;

  addUserMessage: (content: string) => string;
  startAssistantMessage: () => string;
  appendToAssistantMessage: (id: string, chunk: string) => void;
  finishStreaming: () => void;
  setError: (error: string | null) => void;
  setTripId: (tripId: string | null) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  error: null,
  tripId: null,

  addUserMessage: (content) => {
    const id = generateId();
    const message: ChatMessage = {
      id,
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };
    set((state) => ({
      messages: [...state.messages, message],
      error: null,
    }));
    return id;
  },

  startAssistantMessage: () => {
    const id = generateId();
    const message: ChatMessage = {
      id,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    };
    set((state) => ({
      messages: [...state.messages, message],
      isStreaming: true,
    }));
    return id;
  },

  appendToAssistantMessage: (id, chunk) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + chunk } : m
      ),
    })),

  finishStreaming: () => set({ isStreaming: false }),

  setError: (error) => set({ error, isStreaming: false }),

  setTripId: (tripId) => set({ tripId }),

  clearMessages: () => set({ messages: [], error: null }),
}));
