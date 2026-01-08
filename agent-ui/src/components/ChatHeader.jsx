// components/ChatHeader.jsx
import UserMenu from "./UserMenu";

export default function ChatHeader({ onMenu, status }) {
  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
      <button
        onClick={onMenu}
        className="md:hidden text-gray-400"
      >
        ☰
      </button>

      <h1 className="text-white font-semibold text-sm md:text-lg">
        Multi-Agent Orchestrator
      </h1>

      <div className="flex items-center gap-3">
        {status === "running" && (
          <span className="text-xs text-green-400 animate-pulse">Processing</span>
        )}
        <UserMenu />
      </div>
    </header>
  );
}
