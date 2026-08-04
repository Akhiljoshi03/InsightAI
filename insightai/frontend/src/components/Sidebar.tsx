import { NavLink, useNavigate } from "react-router-dom";
import { LayoutGrid, Database, MessageSquare, TrendingUp, FileText, Settings, LogOut } from "lucide-react";
import { useAuthStore } from "../store/authStore";

const items = [
  { to: "/dashboard", label: "Overview", icon: LayoutGrid },
  { to: "/datasets", label: "Datasets", icon: Database },
  { to: "/chat", label: "AI Chat", icon: MessageSquare },
  { to: "/forecasts", label: "Forecasts", icon: TrendingUp },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  return (
    <aside className="w-56 shrink-0 border-r border-border p-3 flex flex-col gap-1 h-screen sticky top-0">
      <div className="flex items-center gap-2 px-2 py-3 mb-2">
        <div className="w-6 h-6 rounded-md bg-gradient-to-br from-violet to-cyan" />
        <span className="font-display font-bold text-sm">InsightAI</span>
      </div>
      {items.map((it) => (
        <NavLink
          key={it.to}
          to={it.to}
          className={({ isActive }) =>
            `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm ${
              isActive ? "bg-violet/15 text-white" : "text-white/60 hover:bg-white/5"
            }`
          }
        >
          <it.icon size={16} /> {it.label}
        </NavLink>
      ))}
      <button
        onClick={() => { logout(); navigate("/login"); }}
        className="mt-auto flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-white/50 hover:bg-white/5"
      >
        <LogOut size={16} /> Sign out
      </button>
    </aside>
  );
}
