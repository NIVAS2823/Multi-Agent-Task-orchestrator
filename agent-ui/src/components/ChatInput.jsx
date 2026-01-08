// components/ChatInput.jsx
export default function ChatInput({ input, setInput, onSend, loading }) {
  return (
    <div className="p-3 border-t border-gray-800 bg-[#0a0a0a]">
      <div className="flex items-end gap-2 bg-[#1a1a1a] rounded-xl p-2">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          rows={1}
          className="flex-1 resize-none bg-transparent text-gray-100 outline-none text-sm max-h-32"
          placeholder="Message…"
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), onSend())}
        />
        <button
          disabled={loading}
          onClick={onSend}
          className="bg-purple-600 px-3 py-2 rounded-lg text-white text-sm"
        >
          Send
        </button>
      </div>
    </div>
  );
}
