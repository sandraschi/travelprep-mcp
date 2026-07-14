import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { Search, ChevronDown, ChevronRight, FileJson } from "lucide-react";
import { useAppStore, type ToolInfo } from "@/stores/app-store";

export default function ToolsHub() {
  const { tools, fetchTools } = useAppStore();
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTools().finally(() => setLoading(false));
  }, [fetchTools]);

  const filtered = useMemo(() => {
    if (!search.trim()) return tools;
    const q = search.toLowerCase();
    return tools.filter(
      t => t.name.toLowerCase().includes(q) || (t.description ?? "").toLowerCase().includes(q)
    );
  }, [tools, search]);

  const hasOperation = (tool: ToolInfo): boolean => {
    const schema = tool.inputSchema;
    if (!schema || typeof schema !== "object") return false;
    const props = (schema as Record<string, unknown>).properties;
    if (!props || typeof props !== "object") return false;
    return Object.keys(props as Record<string, unknown>).includes("operation");
  };

  const toggleTool = (name: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const renderSchema = (schema?: Record<string, unknown>) => {
    if (!schema) return null;
    return (
      <pre className="text-xs text-slate-400 bg-zinc-950 p-3 rounded-lg overflow-x-auto mt-2 max-h-60 overflow-y-auto">
        {JSON.stringify(schema, null, 2)}
      </pre>
    );
  };

  if (loading) {
    return (
      <div data-testid="tools-hub" className="p-6 space-y-4">
        <div className="h-10 rounded-lg bg-zinc-900 border border-zinc-800 animate-pulse" />
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-20 rounded-xl bg-zinc-900 border border-zinc-800 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div data-testid="tools-hub" className="p-6 space-y-4">
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search tools..."
            value={search}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-zinc-900 border border-zinc-700 text-sm text-zinc-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50"
          />
        </div>
        <span className="text-xs text-slate-500">{filtered.length} tool{filtered.length !== 1 ? "s" : ""}</span>
      </div>

      {filtered.length === 0 && (
        <div className="p-8 text-center text-slate-500">
          {search ? "No tools match your search." : "No tools discovered."}
        </div>
      )}

      <div className="space-y-2">
        {filtered.map(tool => {
          const isPortmanteau = hasOperation(tool);
          const isExpanded = expanded.has(tool.name);
          return (
            <div
              key={tool.name}
              className="rounded-xl bg-zinc-900 border border-zinc-800 overflow-hidden"
            >
              <button
                onClick={() => toggleTool(tool.name)}
                className="w-full flex items-center justify-between p-4 hover:bg-zinc-800/50 transition-colors text-left"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {isPortmanteau && (
                    <span className="flex-shrink-0">
                      {isExpanded ? <ChevronDown className="h-4 w-4 text-amber-500" /> : <ChevronRight className="h-4 w-4 text-slate-500" />}
                    </span>
                  )}
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-zinc-100 truncate">{tool.name}</p>
                    {tool.description && (
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{tool.description}</p>
                    )}
                  </div>
                </div>
                {isPortmanteau && (
                  <span className="flex-shrink-0 text-xs text-amber-500/70 bg-amber-500/10 px-2 py-0.5 rounded">
                    portmanteau
                  </span>
                )}
              </button>
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-zinc-800 pt-3">
                  {tool.inputSchema && (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <FileJson className="h-3.5 w-3.5 text-slate-500" />
                        <span className="text-xs font-medium text-slate-500">Input Schema</span>
                      </div>
                      {renderSchema(tool.inputSchema)}
                    </div>
                  )}
                  {!tool.inputSchema && (
                    <p className="text-xs text-slate-600 italic">No schema available</p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
