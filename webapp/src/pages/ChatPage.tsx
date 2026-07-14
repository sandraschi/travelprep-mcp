import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";
import {
  Send,
  Download,
  Eraser,
  MessageSquare,
  User,
  Bot,
} from "lucide-react";
import { SpeakButton } from "@/components/SpeakButton";
import { MicButton } from "@/components/MicButton";
import { initSpeechService } from "@/common/speech";

const OLLAMA = "http://localhost:11434";
const STORAGE_KEY = "travelprep-mcp-chat-history";
const PERSONALITY_KEY = "travelprep-mcp-chat-personality";
const MAX_MESSAGES = 100;
const API_BASE = "/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  ts?: string;
}

interface SkillInfo {
  id: string;
  name: string;
  description: string;
  uri: string;
}

interface Personality {
  id: string;
  label: string;
  prompt: string;
}

const PERSONALITIES: Personality[] = [
  {
    id: "research-assistant",
    label: "Research Assistant",
    prompt: "You are a thorough research assistant specialized in travel preparation. Provide detailed, well-structured answers with references where applicable.",
  },
  {
    id: "expert-reviewer",
    label: "Expert Reviewer",
    prompt: "You are an expert travel reviewer. Critically evaluate travel options, destinations, and itineraries. Highlight pros, cons, and potential issues.",
  },
  {
    id: "quick-summarizer",
    label: "Quick Summarizer",
    prompt: "You are a concise summarizer. Keep responses brief and to the point. Use bullet points when possible.",
  },
  {
    id: "custom",
    label: "Custom",
    prompt: "",
  },
];

function loadHistory(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(messages: Message[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_MESSAGES)));
  } catch {
  }
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(loadHistory);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState("llama3.2");
  const [personality, setPersonality] = useState(() => {
    try { return localStorage.getItem(PERSONALITY_KEY) ?? "research-assistant"; } catch { return "research-assistant"; }
  });
  const [customPrompt, setCustomPrompt] = useState("");
  const [skillName, setSkillName] = useState<string | null>(null);
  const [skillContent, setSkillContent] = useState("");
  const [ollamaUp, setOllamaUp] = useState<boolean | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initSpeechService();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Discover local Ollama/LM Studio (WEBAPP_SOTA_STANDARDS.md "Glom On" pattern)
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/llm/discover`, { signal: AbortSignal.timeout(3000) });
        if (r.ok) {
          const d = await r.json();
          setOllamaUp(Boolean(d.ollama_detected));
          if (d.configured_model) setModel(d.configured_model);
        } else {
          setOllamaUp(false);
        }
      } catch {
        setOllamaUp(false);
      }
    })();
  }, []);

  // Load the primary skill as the base system-prompt (skill-first architecture)
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/skills`);
        if (r.ok) {
          const data = await r.json();
          const skills: SkillInfo[] = data.skills ?? [];
          if (skills.length > 0) {
            const primary = skills[0];
            setSkillName(primary.name);
            const contentR = await fetch(`/skill/${encodeURIComponent(primary.id)}`);
            if (contentR.ok) {
              setSkillContent(await contentR.text());
            }
          }
        }
      } catch {
      }
    })();
  }, []);

  const buildSystemPrompt = useCallback(() => {
    const base = skillContent || "You are a travel preparation assistant. Help users plan trips, find destinations, check requirements, and organize travel logistics.";
    if (personality === "custom") return customPrompt || base;
    const p = PERSONALITIES.find(p => p.id === personality);
    return `${base}\n\n---\n\n## Role\n${p?.prompt ?? ""}`;
  }, [skillContent, personality, customPrompt]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = { role: "user", content: text, ts: new Date().toISOString() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    saveHistory(updated);
    setInput("");
    setLoading(true);

    try {
      const full = [
        { role: "system" as const, content: buildSystemPrompt() },
        ...updated.map(m => ({ role: m.role, content: m.content })),
      ];
      const r = await fetch(`${OLLAMA}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model, messages: full, stream: false }),
      });
      if (!r.ok) throw new Error(`Ollama HTTP ${r.status}`);
      const data = await r.json();
      const assistantMsg: Message = {
        role: "assistant",
        content: data.message?.content ?? "(empty)",
        ts: new Date().toISOString(),
      };
      const final = [...updated, assistantMsg];
      setMessages(final);
      saveHistory(final);
    } catch (e) {
      const errMsg: Message = {
        role: "assistant",
        content: `Error: ${e instanceof Error ? e.message : "Failed to reach Ollama. Make sure it's running on :11434."}`,
        ts: new Date().toISOString(),
      };
      const final = [...updated, errMsg];
      setMessages(final);
      saveHistory(final);
    } finally {
      setLoading(false);
    }
  }, [input, loading, messages, model, buildSystemPrompt]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    saveHistory([]);
  };

  const exportChat = () => {
    if (messages.length === 0) return;
    const lines = messages.map(m => {
      const ts = m.ts ? `[${new Date(m.ts).toLocaleString()}] ` : "";
      return `${ts}${m.role === "user" ? "You" : "Assistant"}: ${m.content}`;
    });
    const blob = new Blob([lines.join("\n\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `travelprep-mcp-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePersonalityChange = (id: string) => {
    setPersonality(id);
    try { localStorage.setItem(PERSONALITY_KEY, id); } catch {}
  };

  const examplePrompts = [
    { category: "Planning", prompts: ["Plan a 2-week trip to Japan", "What do I need for a Schengen visa?"] },
    { category: "Destinations", prompts: ["Best time to visit Bali", "Compare Paris vs Rome for a weekend trip"] },
    { category: "Logistics", prompts: ["Packing checklist for a beach vacation", "How to book cheap flights?"] },
  ];

  const providerColor = ollamaUp === true ? "text-green-500" : ollamaUp === false ? "text-red-500" : "text-slate-500";

  return (
    <div data-testid="chat-page" className="flex flex-col h-full">
      <div data-testid="chat-controls" className="flex items-center justify-between px-6 py-3 border-b border-zinc-800 bg-zinc-900/50">
        <div className="flex items-center gap-4">
          <select
            data-testid="personality-select"
            value={personality}
            onChange={e => handlePersonalityChange(e.target.value)}
            className="bg-zinc-800 text-zinc-200 text-sm border border-zinc-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-amber-500/50"
          >
            {PERSONALITIES.map(p => (
              <option key={p.id} value={p.id}>{p.label}</option>
            ))}
          </select>
          <input
            value={model}
            onChange={e => setModel(e.target.value)}
            aria-label="Model name"
            className="w-32 bg-zinc-800 text-zinc-200 text-xs font-mono border border-zinc-700 rounded-lg px-2 py-1.5 focus:outline-none focus:border-amber-500/50"
          />
          {skillName && (
            <span className="text-xs text-slate-500">skill: {skillName}</span>
          )}
          <span className={`text-xs ${providerColor} flex items-center gap-1`}>
            <span className={`w-1.5 h-1.5 rounded-full ${providerColor.replace("text-", "bg-")}`} />
            {ollamaUp === null ? "Detecting..." : ollamaUp ? "Ollama :11434" : "Ollama not detected"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            data-testid="chat-export"
            onClick={exportChat}
            disabled={messages.length === 0}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-zinc-800 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Export chat"
          >
            <Download className="h-4 w-4" />
          </button>
          <button
            data-testid="chat-clear"
            onClick={clearChat}
            disabled={messages.length === 0}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-zinc-800 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Clear chat"
          >
            <Eraser className="h-4 w-4" />
          </button>
        </div>
      </div>

      {personality === "custom" && (
        <div className="px-6 py-2 border-b border-zinc-800">
          <textarea
            placeholder="Enter custom system prompt..."
            value={customPrompt}
            onChange={e => setCustomPrompt(e.target.value)}
            className="w-full bg-zinc-800 text-zinc-200 text-sm border border-zinc-700 rounded-lg p-2 focus:outline-none focus:border-amber-500/50 resize-none h-20"
          />
        </div>
      )}

      <div data-testid="chat-messages" className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-4">
            <MessageSquare className="h-12 w-12 text-slate-700" />
            <p className="text-sm">Start a conversation about travel preparation.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4 text-amber-400" />
              </div>
            )}
            <div className={`max-w-[70%] ${msg.role === "user" ? "order-1" : ""}`}>
              <div
                className={`p-3 rounded-xl text-sm ${
                  msg.role === "user"
                    ? "bg-amber-500/10 text-zinc-200 rounded-br-sm"
                    : "bg-zinc-800 text-zinc-200 rounded-bl-sm"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
              <div className={`flex items-center gap-1 mt-1 ${msg.role === "user" ? "justify-end" : ""}`}>
                <span className="text-[10px] text-slate-600">
                  {msg.ts ? new Date(msg.ts).toLocaleTimeString() : ""}
                </span>
                {msg.role === "assistant" && <SpeakButton text={msg.content} />}
              </div>
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center flex-shrink-0">
                <User className="h-4 w-4 text-zinc-300" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center">
              <Bot className="h-4 w-4 text-amber-400" />
            </div>
            <div className="p-3 rounded-xl bg-zinc-800">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="px-6 py-3 border-t border-zinc-800 bg-zinc-900/50">
        <div data-testid="example-prompts" className="flex flex-wrap gap-2 mb-3">
          {examplePrompts.map(group => (
            <div key={group.category} className="flex items-center gap-2">
              <span className="text-xs text-slate-600">{group.category}:</span>
              {group.prompts.map(p => (
                <button
                  key={p}
                  onClick={() => setInput(p)}
                  className="text-xs px-2.5 py-1 rounded-full bg-zinc-800 text-slate-400 hover:text-white hover:bg-zinc-700 transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>
          ))}
        </div>
        <div className="flex items-end gap-2">
          <div className="flex-1 relative">
            <textarea
              data-testid="chat-input"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message..."
              rows={1}
              className="w-full bg-zinc-800 text-zinc-200 text-sm border border-zinc-700 rounded-lg pl-3 pr-10 py-2.5 focus:outline-none focus:border-amber-500/50 resize-none"
            />
            <div className="absolute right-2 bottom-2">
              <MicButton input={input} setInput={setInput} />
            </div>
          </div>
          <button
            data-testid="chat-send"
            onClick={sendMessage}
            disabled={!input.trim() || loading || !ollamaUp}
            className="p-2.5 rounded-lg bg-amber-500 text-zinc-900 hover:bg-amber-400 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
