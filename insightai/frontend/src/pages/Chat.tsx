import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Send, Zap } from "lucide-react";
import Sidebar from "../components/Sidebar";
import { api } from "../api/client";

interface Message {
  role: "user" | "assistant";
  text: string;
  confidence?: number;
  stats?: Record<string, unknown>;
}

export default function Chat() {
  const { datasetId } = useParams();
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Ask me anything about this dataset — trends, anomalies, forecasts, or comparisons." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function send() {
    if (!input.trim() || !datasetId) return;
    const question = input;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const { data } = await api.post("/api/chat", { dataset_id: datasetId, message: question });
      setMessages((m) => [...m, { role: "assistant", text: data.text, confidence: data.confidence, stats: data.stats }]);
    } catch (err: any) {
      setMessages((m) => [...m, { role: "assistant", text: err.response?.data?.detail || "Something went wrong." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex bg-bg min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-6 flex flex-col">
        <h1 className="font-display text-xl font-semibold mb-4">AI Chat</h1>
        <div className="flex-1 bg-panel border border-border rounded-2xl flex flex-col overflow-hidden max-w-3xl">
          <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm ${
                  m.role === "user" ? "bg-gradient-to-br from-violet to-violet-dark" : "bg-white/5 border border-border"
                }`}>
                  {m.text}
                  {m.confidence !== undefined && (
                    <div className="flex items-center gap-1.5 text-[11px] text-white/40 mt-2">
                      <Zap size={11} className="text-amber-400" /> Confidence {m.confidence}%
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && <div className="text-xs text-white/30">Thinking…</div>}
            <div ref={endRef} />
          </div>
          <div className="p-3 border-t border-border flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Ask about your data..."
              className="flex-1 px-3 py-2.5 rounded-xl bg-white/5 border border-border text-sm outline-none"
            />
            <button onClick={send} className="w-11 rounded-xl bg-gradient-to-br from-violet to-cyan flex items-center justify-center">
              <Send size={15} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
