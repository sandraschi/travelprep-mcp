import { useCallback, useEffect, useState } from "react";
import { Link, Route, Routes, useLocation } from "react-router-dom";
import {
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Wrench,
  MessageSquare,
  Code2,
  Sun,
  Moon,
} from "lucide-react";
import { useAppStore } from "@/stores/app-store";
import Dashboard from "@/pages/Dashboard";
import ToolsHub from "@/pages/ToolsHub";
import ChatPage from "@/pages/ChatPage";
import ApiDocsPage from "@/pages/ApiDocsPage";

const navLinks = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/tools", label: "Tools Hub", icon: Wrench },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/api-docs", label: "API Docs", icon: Code2 },
];

export default function AppLayout() {
  const { sidebarCollapsed, toggleSidebar, backendOk, fetchHealth, fetchTools, fetchCapabilities } = useAppStore();
  const location = useLocation();
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    fetchHealth();
    fetchTools();
    fetchCapabilities();
  }, [fetchHealth, fetchTools, fetchCapabilities]);

  const toggleTheme = useCallback(() => {
    setTheme(t => {
      const next = t === "dark" ? "light" : "dark";
      document.documentElement.classList.toggle("dark", next === "dark");
      return next;
    });
  }, []);

  const pageTitle = navLinks.find(l => l.to === location.pathname)?.label ?? "Travelprep MCP";

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-200 overflow-hidden">
      <aside
        data-testid="sidebar"
        className={`flex flex-col border-r border-zinc-800 bg-zinc-900/80 backdrop-blur transition-all duration-200 ${
          sidebarCollapsed ? "w-16" : "w-60"
        } flex-shrink-0`}
      >
        <div className="flex items-center justify-between p-4 border-b border-zinc-800">
          {!sidebarCollapsed && (
            <span className="text-lg font-bold text-amber-500 tracking-wide">TP</span>
          )}
          {sidebarCollapsed && (
            <span className="text-lg font-bold text-amber-500 mx-auto">TP</span>
          )}
          <button
            onClick={toggleSidebar}
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-zinc-800 transition-colors"
            title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>
        <nav className="flex-1 py-4 space-y-1 px-2">
          {navLinks.map(link => {
            const active = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                  active
                    ? "bg-amber-500/10 text-amber-400"
                    : "text-slate-400 hover:text-white hover:bg-zinc-800"
                }`}
                title={link.label}
              >
                <link.icon className="h-5 w-5 flex-shrink-0" />
                {!sidebarCollapsed && <span className="text-sm font-medium">{link.label}</span>}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header
          data-testid="topbar"
          className="flex items-center justify-between px-6 py-3 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur flex-shrink-0"
        >
          <h1 className="text-lg font-semibold text-zinc-100">{pageTitle}</h1>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div
                data-testid="backend-dot"
                className={`w-2.5 h-2.5 rounded-full ${
                  backendOk === null
                    ? "bg-gray-500"
                    : backendOk
                    ? "bg-green-500 animate-pulse"
                    : "bg-red-500"
                }`}
              />
              <span className="text-xs text-slate-500">
                {backendOk === null ? "Connecting..." : backendOk ? "Connected" : "Offline"}
              </span>
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-zinc-800 transition-colors"
              title="Toggle theme"
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
          </div>
        </header>

        <main data-testid="content" className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tools" element={<ToolsHub />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/api-docs" element={<ApiDocsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
