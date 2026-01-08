// components/Sidebar.jsx
export default function Sidebar({ open, onClose, sessions }) {
  return (
    <>
      {/* Overlay (mobile only) */}
      {open && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/60 z-40 md:hidden"
        />
      )}

      <aside
        className={`
          fixed md:static z-50
          w-72 h-full bg-[#0f0f0f] border-r border-gray-800
          transform transition-transform duration-300
          ${open ? "translate-x-0" : "-translate-x-full"}
          md:translate-x-0
        `}
      >
        <div className="p-4 font-semibold text-white border-b border-gray-800">
          Chat History
        </div>

        <div className="overflow-y-auto p-2 space-y-2">
          {sessions.map(s => (
            <div
              key={s.id}
              className="p-3 bg-[#1a1a1a] rounded-lg text-sm text-gray-200"
            >
              {s.title}
            </div>
          ))}
        </div>
      </aside>
    </>
  );
}
