// components/ChatLayout.jsx
import Sidebar from "./Sidebar";
import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

export default function ChatLayout(props) {
  return (
    <div className="flex h-screen bg-[#0a0a0a] overflow-hidden">

      {/* Sidebar (desktop static, mobile drawer) */}
      <Sidebar
        open={props.showSidebar}
        onClose={() => props.setShowSidebar(false)}
        sessions={props.sessions}
      />

      {/* Main */}
      <div className="flex-1 flex flex-col">
        <ChatHeader onMenu={() => props.setShowSidebar(true)} status={props.status} />

        <MessageList
          messages={props.messages}
          loading={props.loading}
        />

        <ChatInput
          input={props.input}
          setInput={props.setInput}
          onSend={props.runAgent}
          loading={props.loading}
        />
      </div>
    </div>
  );
}
