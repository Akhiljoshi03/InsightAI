import { useCallback, useState } from "react";
import { Upload } from "lucide-react";
import { api } from "../api/client";

interface Props {
  projectId: string;
  onUploaded: () => void;
}

export default function UploadDropzone({ projectId, onUploaded }: Props) {
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const upload = useCallback(async (files: FileList) => {
    setError(null);
    for (const file of Array.from(files)) {
      const form = new FormData();
      form.append("project_id", projectId);
      form.append("file", file);
      try {
        await api.post("/api/datasets/upload", form, {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (e) => setProgress(e.total ? Math.round((e.loaded / e.total) * 100) : null),
        });
      } catch (err: any) {
        setError(err.response?.data?.detail || `Failed to upload ${file.name}`);
      }
    }
    setProgress(null);
    onUploaded();
  }, [projectId, onUploaded]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); if (e.dataTransfer.files.length) upload(e.dataTransfer.files); }}
      onClick={() => document.getElementById("file-input")?.click()}
      className={`text-center p-9 rounded-2xl border-2 border-dashed cursor-pointer transition ${
        dragging ? "border-cyan bg-cyan/5" : "border-border bg-panel"
      }`}
    >
      <input
        id="file-input"
        type="file"
        multiple
        accept=".csv,.xlsx,.xls,.json"
        className="hidden"
        onChange={(e) => e.target.files && upload(e.target.files)}
      />
      <Upload size={22} className="mx-auto mb-2 text-cyan" />
      <div className="text-sm font-medium">Drop CSV, Excel, or JSON files here</div>
      <div className="text-xs text-white/40 mt-1">or click to browse — multiple files supported</div>
      {progress !== null && <div className="text-xs text-cyan mt-3">Uploading… {progress}%</div>}
      {error && <div className="text-xs text-red-400 mt-3">{error}</div>}
    </div>
  );
}
