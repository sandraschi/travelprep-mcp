import { create } from "zustand";

const API_BASE = "/api";

export interface ToolInfo {
  name: string;
  description?: string;
  inputSchema?: Record<string, unknown>;
}

export interface HealthData {
  status: string;
  server?: string;
  version?: string;
  tool_count?: number;
  uptime_seconds?: number;
  providers?: Record<string, unknown>;
}

async function fetchWithBackoff(url: string, retries = 5): Promise<Response> {
  const delays = [1000, 2000, 4000, 8000, 16000];
  for (let i = 0; i < retries; i++) {
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(5000) });
      return r;
    } catch {
      if (i < delays.length) await new Promise(r => setTimeout(r, delays[i]));
    }
  }
  throw new Error(`Failed to fetch ${url} after ${retries} retries`);
}

interface AppState {
  backendOk: boolean | null;
  backendStatus: "connecting" | "connected" | "offline";
  tools: ToolInfo[];
  capabilities: unknown;
  sidebarCollapsed: boolean;
  fetchHealth: () => Promise<void>;
  fetchTools: () => Promise<void>;
  fetchCapabilities: () => Promise<void>;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  backendOk: null,
  backendStatus: "connecting",
  tools: [],
  capabilities: null,
  sidebarCollapsed: false,

  fetchHealth: async () => {
    try {
      const r = await fetchWithBackoff(`${API_BASE}/health`);
      if (r.ok) {
        set({ backendOk: true, backendStatus: "connected" });
      } else {
        set({ backendOk: false, backendStatus: "offline" });
      }
    } catch {
      set({ backendOk: false, backendStatus: "offline" });
    }
  },

  fetchTools: async () => {
    try {
      const r = await fetch(`${API_BASE}/tools`);
      if (r.ok) {
        const data = await r.json();
        set({ tools: Array.isArray(data) ? data : data.tools ?? [] });
      }
    } catch {
    }
  },

  fetchCapabilities: async () => {
    try {
      const r = await fetch(`${API_BASE}/capabilities`);
      if (r.ok) {
        set({ capabilities: await r.json() });
      }
    } catch {
    }
  },

  toggleSidebar: () => set(s => ({ sidebarCollapsed: !s.sidebarCollapsed })),
}));
