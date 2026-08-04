import { useQuery } from "@tanstack/react-query";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/charts/ChartCard";
import { api } from "../api/client";

// In a real deployment the dashboard aggregates across the user's most
// recently active dataset; this fetches the first project's datasets as an example.
async function fetchDatasets() {
  const { data: projects } = await api.get("/api/projects");
  if (!projects.length) return [];
  const { data: datasets } = await api.get(`/api/datasets/project/${projects[0].id}`);
  return datasets;
}

export default function Dashboard() {
  const { data: datasets, isLoading, isError } = useQuery({
    queryKey: ["datasets"],
    queryFn: fetchDatasets,
  });

  return (
    <div className="flex bg-bg min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="font-display text-xl font-semibold mb-5">Overview</h1>

        {isLoading && <div className="text-white/40 text-sm">Loading your workspace…</div>}
        {isError && <div className="text-red-400 text-sm">Couldn't reach the API. Is the backend running?</div>}

        {!isLoading && !isError && (!datasets || datasets.length === 0) && (
          <div className="text-center py-20 border border-dashed border-border rounded-2xl">
            <div className="text-white/60 text-sm mb-1">No datasets yet</div>
            <div className="text-white/30 text-xs">Upload a CSV, Excel, or JSON file from the Datasets tab to get started.</div>
          </div>
        )}

        {datasets && datasets.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <ChartCard title="Rows per dataset">
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={datasets.map((d: any) => ({ name: d.filename, rows: d.row_count }))}>
                  <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                  <XAxis dataKey="name" stroke="#9599AC" fontSize={11} />
                  <YAxis stroke="#9599AC" fontSize={11} />
                  <Tooltip contentStyle={{ background: "#111116", border: "1px solid rgba(255,255,255,0.08)" }} />
                  <Line type="monotone" dataKey="rows" stroke="#8B5CF6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>
        )}
      </main>
    </div>
  );
}
