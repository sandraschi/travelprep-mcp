import { useCallback, useRef, useState } from "react";
import { ExternalLink, Code2 } from "lucide-react";

const API_BASE = "http://127.0.0.1:11099";

const representativeEndpoints = [
  { method: "GET", path: "/api/health", description: "Server health & status" },
  { method: "GET", path: "/api/tools", description: "List all MCP tools" },
  { method: "GET", path: "/api/capabilities", description: "Server capabilities" },
  { method: "GET", path: "/api/skills", description: "Available skills" },
  { method: "POST", path: "/api/chat/stream", description: "Chat completion" },
  { method: "GET", path: "/api/llm/discover", description: "LLM provider discovery" },
];

export default function ApiDocsPage() {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [docsView, setDocsView] = useState<"swagger" | "redoc">("swagger");

  const injectDarkTheme = useCallback(() => {
    try {
      const iframe = iframeRef.current;
      if (!iframe || !iframe.contentDocument) return;
      const style = iframe.contentDocument.createElement("style");
      style.textContent = `
        :root {
          --bg: #09090b !important;
          --bg-paper: #18181b !important;
          --bg-code: #27272a !important;
          --text: #e4e4e7 !important;
          --text-secondary: #a1a1aa !important;
          --border: #27272a !important;
          --primary: #f59e0b !important;
        }
        body { background: var(--bg) !important; color: var(--text) !important; }
        .opblock-summary-method { border-radius: 4px !important; }
        .scheme-container, .information-container, .opblock, .opblock-tag, .model-box {
          background: var(--bg-paper) !important;
          border-color: var(--border) !important;
        }
        .opblock-summary { border-bottom-color: var(--border) !important; }
        .opblock-summary-description { color: var(--text-secondary) !important; }
        .model-title { color: var(--text) !important; }
        .parameter__name, .parameter__type, .parameter__in {
          color: var(--text-secondary) !important;
        }
        .btn { border-color: var(--border) !important; }
        select, input { background: var(--bg-code) !important; color: var(--text) !important; border-color: var(--border) !important; }
        .topbar { display: none !important; }
        .version; { color: var(--text-secondary) !important; }
      `;
      iframe.contentDocument.head.appendChild(style);
    } catch {
    }
  }, []);

  const docsUrl = docsView === "swagger" ? `${API_BASE}/docs` : `${API_BASE}/redoc`;

  return (
    <div data-testid="api-docs" className="p-6 space-y-4 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Code2 className="h-5 w-5 text-amber-500" />
          <h2 className="text-lg font-semibold text-zinc-100">API Documentation</h2>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg overflow-hidden border border-zinc-700">
            <button
              onClick={() => setDocsView("swagger")}
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                docsView === "swagger" ? "bg-amber-500/20 text-amber-400" : "bg-zinc-800 text-slate-400 hover:text-white"
              }`}
            >
              Swagger UI
            </button>
            <button
              onClick={() => setDocsView("redoc")}
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                docsView === "redoc" ? "bg-amber-500/20 text-amber-400" : "bg-zinc-800 text-slate-400 hover:text-white"
              }`}
            >
              ReDoc
            </button>
          </div>
          <a
            href={docsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-zinc-800 text-slate-400 hover:text-white hover:bg-zinc-700 transition-colors"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            Open in browser
          </a>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">Quick Reference</p>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {representativeEndpoints.map(ep => (
            <div
              key={ep.path}
              className="flex-shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-800 border border-zinc-700"
            >
              <span
                className={`text-xs font-mono font-bold px-1.5 py-0.5 rounded ${
                  ep.method === "GET"
                    ? "text-green-400 bg-green-500/10"
                    : ep.method === "POST"
                    ? "text-blue-400 bg-blue-500/10"
                    : "text-amber-400 bg-amber-500/10"
                }`}
              >
                {ep.method}
              </span>
              <span className="text-xs text-zinc-300 font-mono">{ep.path}</span>
              <span className="text-xs text-slate-600 hidden md:inline">{ep.description}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 rounded-xl overflow-hidden border border-zinc-800 min-h-0">
        <iframe
          ref={iframeRef}
          src={docsUrl}
          className="w-full h-full bg-zinc-950"
          title="API Documentation"
          onLoad={injectDarkTheme}
        />
      </div>
    </div>
  );
}
