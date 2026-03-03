"use client";

import { ChatWindow } from "@/components/chat/ChatWindow";

export default function ChatPage() {
  return (
    <div className="flex h-[calc(100vh-64px-1px)] flex-col">
      <ChatWindow />
    </div>
  );
}
