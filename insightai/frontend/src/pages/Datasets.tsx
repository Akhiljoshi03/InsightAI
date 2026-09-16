import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import UploadDropzone from "../components/UploadDropzone";
import ChartCard from "../components/charts/ChartCard";
import { api } from "../api/client";
import { useDefaultProject } from "../lib/useProject";

export default function Datasets() {
  const queryClient = useQueryClient();
  const { data: project, isLoading: projectLoading } = useDefaultProject();

  const { data: datasets, isLoading: datasetsLoading } = useQuery({
    queryKey: ["datasets", project?.id],
    queryFn: async () => (await api.get(`/api/datasets/project/${project.id}`)).data,
    enabled: !!project?.id,
  });

  const refresh = () => queryClient.invalidateQueries({ queryKey: ["datasets", project?.id] });

  return (
    <div className="flex bg-bg min-h-screen text-white">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="font-display text-xl font-semibold mb-5">Datasets</h1>

        {(projectLoading || datasetsLoading) && (
          <div className="text-white/40 text-sm mb-4">Loading…</div>
        )}

        {project && (
          <div className="mb-6">
            <UploadDropzone projectId={project.id} onUploaded={refresh} />
          </div>
        )}

        {datasets && datasets.length > 0 && (
          <ChartCard title="Your datasets">
            <div className="flex flex-col divide-y divide-border">
              {datasets.map((d: any) => (
                <Link
                  key={d.id}
                  to={`/datasets/${d.id}`}
                  className="flex items-center justify-between py-3 hover:bg-white/5 rounded-lg px-2 -mx-2 transition"
                >
                  <div>
                    <div className="text-sm font-medium">{d.filename}</div>
                    <div className="text-xs text-white/40 font-mono mt-0.5">
                      {d.row_count} rows · {d.column_count} columns · {d.status}
                    </div>
                  </div>
                  <span className="text-xs text-white/30 uppercase font-mono">{d.file_type}</span>
                </Link>
              ))}
            </div>
          </ChartCard>
        )}

        {datasets && datasets.length === 0 && (
          <div className="text-center py-12 text-sm text-white/40">
            No datasets yet — upload one above to get started.
          </div>
        )}
      </main>
    </div>
  );
}
