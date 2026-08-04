import { create } from "zustand";

export interface Dataset {
  id: string;
  filename: string;
  file_type: string;
  row_count: number;
  column_count: number;
  status: string;
  profile?: Record<string, unknown>;
}

interface DatasetState {
  activeDatasetId: string | null;
  datasets: Dataset[];
  setActiveDataset: (id: string | null) => void;
  setDatasets: (datasets: Dataset[]) => void;
}

export const useDatasetStore = create<DatasetState>((set) => ({
  activeDatasetId: null,
  datasets: [],
  setActiveDataset: (id) => set({ activeDatasetId: id }),
  setDatasets: (datasets) => set({ datasets }),
}));
