export default function AgentTimeline({ events }) {
  return (
    <div className="bg-[#111] border border-gray-800 rounded-xl p-4 mb-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-3">
        Agent Orchestration
      </h3>

      <div className="space-y-2">
        {events.map((e, i) => (
          <div key={i} className="flex items-start gap-3 text-sm">
            <span className="text-purple-400 font-mono w-20">
              {e.agent}
            </span>
            <span className="text-gray-300">
              {e.action}
              {e.detail && (
                <span className="text-gray-500"> — {e.detail}</span>
              )}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
