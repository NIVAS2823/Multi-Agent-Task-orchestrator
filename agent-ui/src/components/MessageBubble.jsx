import { useState } from "react";

export default function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.type === "user";
  const isError = message.type === "error";

  const copyText = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {}
  };

  return (
    <div
      className={`
        flex w-full
        ${isUser ? "justify-end" : "justify-start"}
      `}
    >
      {/* Assistant Avatar (hidden on mobile for space) */}
      {!isUser && !isError && (
        <div className="hidden sm:flex mr-2">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg
                          flex items-center justify-center text-white font-bold shadow">
            M
          </div>
        </div>
      )}

      {/* Bubble */}
      <div
        className={`
          max-w-[90%] sm:max-w-[75%] md:max-w-[65%]
          rounded-2xl px-4 py-3 text-sm sm:text-base
          break-words whitespace-pre-wrap
          ${
            isUser
              ? "bg-gradient-to-br from-purple-600 to-pink-600 text-white"
              : isError
              ? "bg-red-950/50 text-red-300 border border-red-800/50"
              : "bg-[#1a1a1a] text-gray-100 border border-gray-800"
          }
        `}
      >
        {/* Content */}
        <div>{message.content}</div>

        {/* Footer */}
        <div className="flex items-center justify-between gap-3 mt-2 pt-2 border-t border-gray-700/30 text-xs">
          <button
            onClick={copyText}
            className={`
              transition-colors
              ${isUser ? "text-white/70 hover:text-white" : "text-gray-500 hover:text-gray-300"}
            `}
          >
            {copied ? "Copied ✓" : "Copy"}
          </button>

          <span
            className={`
              ${isUser ? "text-white/50" : "text-gray-600"}
            `}
          >
            {message.timestamp?.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>
      </div>

      {/* User Avatar (mobile-friendly) */}
      {isUser && (
        <div className="hidden sm:flex ml-2">
          <div className="w-8 h-8 bg-gray-700 rounded-lg flex items-center justify-center text-white shadow">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
          </div>
        </div>
      )}
    </div>
  );
}
