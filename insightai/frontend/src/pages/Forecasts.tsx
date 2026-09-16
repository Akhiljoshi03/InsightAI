import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/charts/ChartCard";
import { api } from "../api/client";
import { useDefaultProject } from "../lib/useProject";

export default function Forecasts() {
  const { data: project } = useDefaultProject();
  const { data: datasets } = useQuery({
    queryKey: ["datasets", project?.id],
    queryFn: async () => (await api.get(`/api/datasets/project/${project.id}`)).data,
    enabled: !!project?.id,
  });

  const [datasetId, setDatasetId] = useState("");
  const [dateColumn, setDateColumn] = useState("");
  const [valueColumn, setValueColumn] = useState("");
  const [periods, setPeriods] = useState(6);

  const selected = datasets?.find((d: any) => d.id === datasetId);
  const columns: string[] = selected?.profile?.columns?.map((c: any) => c.name) || [];

  const mutation = useMutation({
    mutationFn: async () =>
      (await api.post("/api/forecast", { dataset_id: datasetId, date_column: dateColumn, value_column: valueColumn, periods })).data,
  });

  const chartData = mutation.data
    ? [
        ...mutation.data.history.map((h: any) => ({ date: h.date, actual: h.value })),
        ...mutation.data.forecast.map((f: any) => ({ date: f.date, forecast: f.forecast, lower: f.lower, upper: f.upper })),
      ]
    : [];

  return (
    <div className="flex bg-bg min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="font-display text-xl font-semibold mb-5">Forecasts</h1>

        {(!datasets || datasets.length === 0) && (
          <div className="text-center py-12 text-sm text-white/40">
            Upload a dataset from the Datasets tab first.
          </div>
        )}

        {datasets && datasets.length > 0 && (
          <ChartCard title="Configure forecast">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              <select
                value={datasetId}
                onChange={(e) => { setDatasetId(e.target.value); setDateColumn(""); setValueColumn(""); }}
                className="px-3 py-2 rounded-lg bg-white/5 border border-border text-sm"
              >
                <option value="">Select dataset…</option>
                {datasets.map((d: any) => (
                  <option key={d.id} value={d.id}>{d.filename}</option>
                ))}
              </select>
              <select value={dateColumn} onChange={(e) => setDateColumn(e.target.value)} className="px-3 py-2 rounded-lg bg-white/5 border border-border text-sm" disabled={!columns.length}>
                <option value="">Date column…</option>
                {columns.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <select value={valueColumn} onChange={(e) => setValueColumn(e.target.value)} className="px-3 py-2 rounded-lg bg-white/5 border border-border text-sm" disabled={!columns.length}>
                <option value="">Value column…</option>
                {columns.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <input
                type="number"
                min={1}
                max={24}
                value={periods}
                onChange={(e) => setPeriods(Number(e.target.value))}
                className="px-3 py-2 rounded-lg bg-white/5 border border-border text-sm"
                placeholder="Periods ahead"
              />
            </div>
            <button
              onClick={() => mutation.mutate()}
              disabled={!datasetId || !dateColumn || !valueColumn || mutation.isPending}
              className="px-4 py-2 rounded-lg bg-gradient-to-br from-violet to-violet-dark text-sm font-semibold disabled:opacity-40"
            >
              {mutation.isPending ? "Forecasting…" : "Run forecast"}
            </button>
            {mutation.isError && (
              <div className="text-xs text-red-400 mt-3">
                {(mutation.error as any)?.response?.data?.detail || "Forecast failed — try a dataset with a real date column and at least 4 periods of history."}
              </div>
            )}
          </ChartCard>
        )}

        {mutation.data && (
          <div className="mt-5">
            <ChartCard title="History + forecast" subtitle={`Trend slope: ${mutation.data.trend_slope}`}>
              <ResponsiveContainer width="100%" height={320}>
                <LineChart data={chartData}>
                  <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
                  <XAxis dataKey="date" stroke="#9599AC" fontSize={11} />
                  <YAxis stroke="#9599AC" fontSize={11} />
                  <Tooltip contentStyle={{ background: "#111116", border: "1px solid rgba(255,255,255,0.08)" }} />
                  <Legend />
                  <Line type="monotone" dataKey="actual" stroke="#22D3EE" strokeWidth={2} dot={false} name="Actual" />
                  <Line type="monotone" dataKey="forecast" stroke="#8B5CF6" strokeWidth={2} dot={false} name="Forecast" />
                  <Line type="monotone" dataKey="upper" stroke="#8B5CF6" strokeWidth={1} strokeDasharray="4 4" dot={false} name="Upper bound" />
                  <Line type="monotone" dataKey="lower" stroke="#8B5CF6" strokeWidth={1} strokeDasharray="4 4" dot={false} name="Lower bound" />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>
        )}
      </main>
    </div>
  );
}
