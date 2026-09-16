import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/charts/ChartCard";
import { api } from "../api/client";
import { useDefaultProject } from "../lib/useProject";

const SECTION_LABELS: Record<string, string> = {
  executive_summary: "Executive Summary",
  dataset_overview: "Dataset Overview",
  insights: "Key Insights",
  opportunities: "Business Opportunities",
  risks: "Risks",
  recommendations: "Recommendations",
};

export default function Reports() {
  const { data: project } = useDefaultProject();
  const { data: datasets } = useQuery({
    queryKey: ["datasets", project?.id],
    queryFn: async () => (await api.get(`/api/datasets/project/${project.id}`)).data,
    enabled: !!project?.id,
  });

  const [datasetId, setDatasetId] = useState("");
  const [title, setTitle] = useState("Executive Report");

  const mutation = useMutation({
    mutationFn: async () =>
      (await api.post("/api/reports/generate", { dataset_id: datasetId, title })).data,
  });

  const exportReport = (fmt: "pdf" | "xlsx" | "csv") => {
    if (!mutation.data?.id) return;
    window.open(`${api.defaults.baseURL}/api/reports/${mutation.data.id}/export/${fmt}`, "_blank");
  };

  return (
    <div className="flex bg-bg min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="font-display text-xl font-semibold mb-5">Reports</h1>

        {(!datasets || datasets.length === 0) && (
          <div className="text-center py-12 text-sm text-white/40">
            Upload a dataset from the Datasets tab first.
          </div>
        )}

        {datasets && datasets.length > 0 && (
          <ChartCard title="Generate a report">
            <p className="text-xs text-white/40 mb-3">
              Report writing calls the OpenAI API — this needs OPENAI_API_KEY set on the backend to work.
            </p>
            <div className="flex flex-wrap gap-3 mb-4">
              <select value={datasetId} onChange={(e) => setDatasetId(e.target.value)} className="px-3 py-2 rounded-lg bg-white/5 border border-border text-sm">
                <option value="">Select dataset…</option>
                {datasets.map((d: any) => (
                  <option key={d.id} value={d.id}>{d.filename}</option>
                ))}
              </select>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Report title"
                className="px-3 py-2 rounded-lg bg-white/5 border border-border text-sm flex-1 min-w-[180px]"
              />
              <button
                onClick={() => mutation.mutate()}
                disabled={!datasetId || mutation.isPending}
                className="px-4 py-2 rounded-lg bg-gradient-to-br from-violet to-violet-dark text-sm font-semibold disabled:opacity-40"
              >
                {mutation.isPending ? "Generating…" : "Generate"}
              </button>
            </div>
            {mutation.isError && (
              <div className="text-xs text-red-400">
                {(mutation.error as any)?.response?.data?.detail || "Report generation failed."}
              </div>
            )}
          </ChartCard>
        )}

        {mutation.data && (
          <div className="mt-5 flex flex-col gap-4">
            <div className="flex gap-2">
              <button onClick={() => exportReport("pdf")} className="px-3 py-1.5 rounded-lg border border-border text-xs hover:bg-white/5">Export PDF</button>
              <button onClick={() => exportReport("xlsx")} className="px-3 py-1.5 rounded-lg border border-border text-xs hover:bg-white/5">Export XLSX</button>
              <button onClick={() => exportReport("csv")} className="px-3 py-1.5 rounded-lg border border-border text-xs hover:bg-white/5">Export CSV</button>
            </div>
            {Object.entries(mutation.data.content || {}).map(([key, value]) => (
              <ChartCard key={key} title={SECTION_LABELS[key] || key}>
                {Array.isArray(value) ? (
                  <ul className="list-disc list-inside text-sm text-white/70 space-y-1">
                    {value.map((item: any, i: number) => <li key={i}>{String(item)}</li>)}
                  </ul>
                ) : (
                  <p className="text-sm text-white/70 whitespace-pre-wrap">{String(value)}</p>
                )}
              </ChartCard>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
