import { useCallback, useEffect, useState } from "react";
import { RefreshCw, Server, Wrench, Clock, Activity } from "lucide-react";
import { useAppStore, type HealthData } from "@/stores/app-store";

const API_BASE = "/api";

async function fetchWithBackoff(url: string, maxRetries = 5): Promise<Response> {
  const delays = [1000, 2000, 4000, 8000, 16000];
  for (let i = 0; i < maxRetries; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(5000) });
      if (r.ok) return r;
    } catch {
    }
    if (i < delays.length) await new Promise(r => setTimeout(r, delays[i]));
  }
  throw new Error(`Failed after ${maxRetries} retries`);
}

export default function Dashboard() {
  const { backendOk } = useAppStore();
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [restarting, setRestarting] = useState(false);
  const [capabilities, setCapabilities] = useState<Record<string, number> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    try {
      const r = await fetchWithBackoff(`${API_BASE}/health`);
      const data: HealthData = await r.json();
      setHealth(data);
      useAppStore.setState({ backendOk: true, backendStatus: "connected" });
      setError(null);
    } catch {
      useAppStore.setState({ backendOk: false, backendStatus: "offline" });
      setError("Backend unreachable");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCaps = useCallback(async () => {
    try {
      const r = await fetch(`${API_BASE}/capabilities`);
      if (r.ok) {
        const data = await r.json();
        if (data && typeof data === "object") {
          const counts: Record<string, number> = {};
          for (const [k, v] of Object.entries(data)) {
            if (Array.isArray(v)) counts[k] = v.length;
            else if (typeof v === "object" && v !== null) counts[k] = Object.keys(v).length;
            else counts[k] = 1;
          }
          setCapabilities(counts);
        }
      }
    } catch {
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    fetchCaps();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth, fetchCaps]);

  useEffect(() => {
    let unlisten: (() => void) | undefined;
    (async () => {
      try {
        const { listen } = await import("@tauri-apps/api/event");
        unlisten = await listen<string>("backend-status", (event) => {
          if (event.payload === "ready") {
            fetchHealth();
          } else if (typeof event.payload === "string" && event.payload.startsWith("error:")) {
            useAppStore.setState({ backendOk: false, backendStatus: "offline" });
          }
        });
      } catch {
      }
    })();
    return () => { if (unlisten) unlisten(); };
  }, [fetchHealth]);

  const restartBackend = useCallback(async () => {
    setRestarting(true);
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      await invoke("start_backend");
    } catch {
      useAppStore.setState({ backendOk: false, backendStatus: "offline" });
    } finally {
      setRestarting(false);
    }
  }, []);

  const formatUptime = (seconds?: number) => {
    if (!seconds) return "—";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}h ${m}m`;
  };

  if (loading) {
    return (
      <div data-testid="dashboard" className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-28 rounded-xl bg-zinc-900 border border-zinc-800 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div data-testid="dashboard" className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-zinc-100">Dashboard</h2>
        <div className="flex items-center gap-3">
          <div
            data-testid="backend-dot"
            className={`w-3 h-3 rounded-full ${
              backendOk === null ? "bg-gray-500" : backendOk ? "bg-green-500 animate-pulse" : "bg-red-500"
            }`}
          />
          <span className="text-sm text-slate-400">
            {backendOk === null ? "Connecting..." : backendOk ? "Connected" : "Offline"}
          </span>
          {!backendOk && (
            <button
              onClick={restartBackend}
              disabled={restarting}
              className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${restarting ? "animate-spin" : ""}`} />
              {restarting ? "Restarting..." : "Restart Backend"}
            </button>
          )}
          <button
            onClick={fetchHealth}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-zinc-800 transition-colors"
            title="Refresh"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div data-testid="kpi-server" className="p-5 rounded-xl bg-zinc-900 border border-zinc-800">
          <div className="flex items-center gap-3 mb-3">
            <Server className="h-5 w-5 text-amber-500" />
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Server</span>
          </div>
          <p className="text-lg font-semibold text-zinc-100">{health?.server ?? "Travelprep MCP"}</p>
          <p className="text-xs text-slate-500 mt-1">v{health?.version ?? "—"}</p>
        </div>

        <div data-testid="kpi-tools" className="p-5 rounded-xl bg-zinc-900 border border-zinc-800">
          <div className="flex items-center gap-3 mb-3">
            <Wrench className="h-5 w-5 text-amber-500" />
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Tools</span>
          </div>
          <p className="text-lg font-semibold text-zinc-100">{health?.tool_count ?? "—"}</p>
          <p className="text-xs text-slate-500 mt-1">registered tools</p>
        </div>

        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800">
          <div className="flex items-center gap-3 mb-3">
            <Clock className="h-5 w-5 text-amber-500" />
            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Uptime</span>
          </div>
          <p className="text-lg font-semibold text-zinc-100">{formatUptime(health?.uptime_seconds)}</p>
          <p className="text-xs text-slate-500 mt-1">since last restart</p>
        </div>
      </div>

      {capabilities && (
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800">
          <div className="flex items-center gap-3 mb-4">
            <Activity className="h-5 w-5 text-amber-500" />
            <span className="text-sm font-medium text-zinc-200">Capabilities</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(capabilities).map(([key, count]) => (
              <div key={key} className="p-3 rounded-lg bg-zinc-800/50">
                <p className="text-sm font-semibold text-zinc-100">{count}</p>
                <p className="text-xs text-slate-500 capitalize">{key.replace(/_/g, " ")}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {health?.providers && typeof health.providers === "object" && Object.keys(health.providers).length > 0 && (
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800">
          <span className="text-sm font-medium text-zinc-200 mb-3 block">Providers</span>
          <div className="space-y-2">
            {Object.entries(health.providers).map(([name, status]) => (
              <div key={name} className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${status ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-sm text-zinc-300 capitalize">{name}</span>
                <span className="text-xs text-slate-500">{status ? "OK" : "Unavailable"}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
