// components/MessageList.jsx
import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

export default function MessageList({ messages, loading }) {
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto px-3 md:px-6 py-4 space-y-4">
      {messages.map((m, i) => (
        <MessageBubble key={i} message={m} />
      ))}

      {loading && (
        <div className="text-gray-500 text-sm">Thinking…</div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
