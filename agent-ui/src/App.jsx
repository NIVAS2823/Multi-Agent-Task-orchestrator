import { useState, useRef, useEffect } from "react";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("idle");
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  async function runAgent() {
    if (!input.trim()) return;

    const userMessage = { type: "user", content: input.trim(), timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setStatus("running");

    try {
      const response = await fetch("http://localhost:8000/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_goal: userMessage.content }),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const data = await response.json();
      const assistantMessage = { 
        type: "assistant", 
        content: data.final_output || "No output received",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setStatus("completed");
    } catch (err) {
      const errorMessage = { 
        type: "error", 
        content: err.message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setStatus("error");
    } finally {
      setLoading(false);
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      runAgent();
    }
  };

  const copyMessage = (content) => {
    navigator.clipboard.writeText(content);
  };

  const handleExampleClick = (example) => {
    setInput(example);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <header className="sticky top-0 z-50 bg-[#0a0a0a] border-b border-gray-800">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-purple-500/20">
              M
            </div>
            <h1 className="text-lg font-semibold text-white">Multi-Agent Orchestrator</h1>
          </div>
          {status === "running" && (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
              <span>Processing...</span>
            </div>
          )}
        </div>
      </header>

      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 py-6">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl flex items-center justify-center mb-6 shadow-2xl shadow-purple-500/30">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h2 className="text-3xl font-bold text-white mb-3">
                  What can I help you with?
                </h2>
                <p className="text-gray-400 mb-8 max-w-md">
                  Describe your task and our AI agents will collaborate to plan, execute, and review the work.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full max-w-2xl">
                  {[
                    { icon: "📊", text: "Analyze sales data from Q4", color: "from-blue-900/40 to-cyan-900/40 border-blue-700/50" },
                    { icon: "🔍", text: "Research latest AI trends", color: "from-purple-900/40 to-pink-900/40 border-purple-700/50" },
                    { icon: "📝", text: "Create a comprehensive report", color: "from-green-900/40 to-emerald-900/40 border-green-700/50" }
                  ].map((example, i) => (
                    <button
                      key={i}
                      onClick={() => handleExampleClick(example.text)}
                      className={`bg-gradient-to-br ${example.color} border rounded-xl p-4 text-left hover:shadow-lg hover:shadow-purple-500/10 transition-all duration-200 hover:scale-105 hover:border-gray-600`}
                    >
                      <div className="text-2xl mb-2">{example.icon}</div>
                      <div className="text-sm text-gray-300 font-medium">{example.text}</div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div key={index} className={`flex gap-4 ${message.type === "user" ? "justify-end" : ""}`}>
                    {message.type !== "user" && (
                      <div className="w-8 h-8 flex-shrink-0 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-purple-500/20">
                        M
                      </div>
                    )}
                    <div className={`flex-1 max-w-3xl ${message.type === "user" ? "flex justify-end" : ""}`}>
                      <div className={`rounded-2xl px-5 py-3 ${
                        message.type === "user" 
                          ? "bg-gradient-to-br from-purple-600 to-pink-600 text-white ml-12 shadow-lg shadow-purple-500/20" 
                          : message.type === "error"
                          ? "bg-red-950/50 text-red-300 border border-red-800/50"
                          : "bg-[#1a1a1a] text-gray-100 border border-gray-800"
                      }`}>
                        <div className="whitespace-pre-wrap break-words">{message.content}</div>
                        <div className="flex items-center gap-3 mt-2 pt-2 border-t border-gray-700/30">
                          <button 
                            onClick={() => copyMessage(message.content)}
                            className={`text-xs transition-colors ${
                              message.type === "user" 
                                ? "text-white/70 hover:text-white" 
                                : "text-gray-500 hover:text-gray-300"
                            }`}
                            title="Copy message"
                          >
                            Copy
                          </button>
                          <span className={`text-xs ${
                            message.type === "user" ? "text-white/50" : "text-gray-600"
                          }`}>
                            {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                          </span>
                        </div>
                      </div>
                    </div>
                    {message.type === "user" && (
                      <div className="w-8 h-8 flex-shrink-0 bg-gray-700 rounded-lg flex items-center justify-center text-white shadow-lg">
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                        </svg>
                      </div>
                    )}
                  </div>
                ))}
                
                {loading && (
                  <div className="flex gap-4">
                    <div className="w-8 h-8 flex-shrink-0 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-purple-500/20">
                      M
                    </div>
                    <div className="flex-1 max-w-3xl">
                      <div className="bg-[#1a1a1a] border border-gray-800 rounded-2xl px-5 py-4">
                        <div className="flex gap-1">
                          {[0, 1, 2].map(i => (
                            <div
                              key={i}
                              className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                              style={{ animationDelay: `${i * 0.15}s` }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-gray-800 bg-[#0a0a0a]">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="relative bg-[#1a1a1a] border border-gray-700 rounded-2xl shadow-lg focus-within:border-purple-500 focus-within:ring-2 focus-within:ring-purple-500/30 transition-all">
              <textarea
                ref={textareaRef}
                className="w-full px-4 py-3 pr-12 bg-transparent resize-none outline-none text-gray-100 placeholder-gray-500"
                rows="1"
                placeholder="Message Multi-Agent Orchestrator..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                disabled={loading}
                style={{ maxHeight: '200px' }}
              />
              <button 
                onClick={runAgent}
                disabled={!input.trim() || loading}
                className="absolute right-2 bottom-2 w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white rounded-lg flex items-center justify-center transition-all shadow-lg shadow-purple-500/30 disabled:shadow-none"
              >
                {loading ? (
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14m-7-7l7 7-7 7" />
                  </svg>
                )}
              </button>
            </div>
            <p className="text-xs text-gray-600 text-center mt-2">
              Press Enter to send • Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;