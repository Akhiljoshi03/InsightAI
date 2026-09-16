import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import ChartCard from "../components/charts/ChartCard";
import { api } from "../api/client";
import { useDefaultProject } from "../lib/useProject";

export default function ChatIndex() {
  const { data: project } = useDefaultProject();
  const { data: datasets, isLoading } = useQuery({
    queryKey: ["datasets", project?.id],
    queryFn: async () => (await api.get(`/api/datasets/project/${project.id}`)).data,
    enabled: !!project?.id,
  });

  return (
    <div className="flex bg-bg min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="font-display text-xl font-semibold mb-5">AI Chat</h1>

        {isLoading && <div className="text-white/40 text-sm">Loading…</div>}

        {datasets && datasets.length === 0 && (
          <div className="text-center py-12 text-sm text-white/40">
            Upload a dataset from the Datasets tab to start chatting with it.
          </div>
        )}

        {datasets && datasets.length > 0 && (
          <ChartCard title="Pick a dataset to chat with">
            <p className="text-xs text-white/40 mb-3">
              This uses the OpenAI API — it needs OPENAI_API_KEY set on the backend to respond.
            </p>
            <div className="flex flex-col divide-y divide-border">
              {datasets.map((d: any) => (
                <Link
                  key={d.id}
                  to={`/chat/${d.id}`}
                  className="flex items-center justify-between py-3 hover:bg-white/5 rounded-lg px-2 -mx-2 transition"
                >
                  <div className="text-sm font-medium">{d.filename}</div>
                  <span className="text-xs text-white/30 font-mono">{d.row_count} rows</span>
                </Link>
              ))}
            </div>
          </ChartCard>
        )}
      </main>
    </div>
  );
}
