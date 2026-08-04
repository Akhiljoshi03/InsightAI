import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/charts/ChartCard";
import { api } from "../api/client";

export default function DatasetView() {
  const { id } = useParams();
  const { data: dataset, isLoading } = useQuery({
    queryKey: ["dataset", id],
    queryFn: async () => (await api.get(`/api/datasets/${id}`)).data,
    enabled: !!id,
  });

  const profile = dataset?.profile;

  return (
    <div className="flex bg-bg min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-6">
        {isLoading && <div className="text-white/40 text-sm">Loading dataset…</div>}
        {dataset && (
          <>
            <h1 className="font-display text-xl font-semibold mb-1">{dataset.filename}</h1>
            <p className="text-xs text-white/40 font-mono mb-6">
              {dataset.row_count} rows · {dataset.column_count} columns · status: {dataset.status}
            </p>

            {profile && (
              <ChartCard title="Column profile">
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead className="text-white/40 border-b border-border">
                      <tr>
                        <th className="text-left py-2 pr-4">Column</th>
                        <th className="text-left py-2 pr-4">Type</th>
                        <th className="text-left py-2 pr-4">Null %</th>
                        <th className="text-left py-2 pr-4">Unique</th>
                      </tr>
                    </thead>
                    <tbody>
                      {profile.columns?.map((c: any) => (
                        <tr key={c.name} className="border-b border-border/50">
                          <td className="py-2 pr-4 font-medium">{c.name}</td>
                          <td className="py-2 pr-4 font-mono text-white/60">{c.dtype}</td>
                          <td className="py-2 pr-4 font-mono text-white/60">{c.null_pct}%</td>
                          <td className="py-2 pr-4 font-mono text-white/60">{c.unique_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </ChartCard>
            )}
          </>
        )}
      </main>
    </div>
  );
}
