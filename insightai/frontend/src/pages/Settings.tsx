import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/charts/ChartCard";
import { useAuthStore } from "../store/authStore";

export default function Settings() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  return (
    <div className="flex bg-bg min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-6 max-w-xl">
        <h1 className="font-display text-xl font-semibold mb-5">Settings</h1>

        <ChartCard title="Account">
          <div className="flex flex-col gap-3 text-sm">
            <div className="flex justify-between border-b border-border/50 pb-2">
              <span className="text-white/40">Name</span>
              <span>{user?.full_name || "—"}</span>
            </div>
            <div className="flex justify-between border-b border-border/50 pb-2">
              <span className="text-white/40">Email</span>
              <span>{user?.email}</span>
            </div>
            <div className="flex justify-between border-b border-border/50 pb-2">
              <span className="text-white/40">Plan</span>
              <span className="capitalize">{user?.plan}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/40">Role</span>
              <span>{user?.is_admin ? "Admin" : "Member"}</span>
            </div>
          </div>
        </ChartCard>

        <div className="mt-5">
          <button
            onClick={() => { logout(); navigate("/login"); }}
            className="px-4 py-2 rounded-lg border border-border text-sm hover:bg-white/5"
          >
            Sign out
          </button>
        </div>
      </main>
    </div>
  );
}
