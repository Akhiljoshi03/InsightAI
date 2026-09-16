import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";

// The backend requires datasets to belong to a "project", but there's no
// project-creation UI yet. This hook transparently fetches the user's first
// project, or creates one called "My Project" the first time they need it.
export function useDefaultProject() {
  const queryClient = useQueryClient();
  return useQuery({
    queryKey: ["default-project"],
    queryFn: async () => {
      const { data: projects } = await api.get("/api/projects");
      if (projects.length > 0) return projects[0];
      const { data: project } = await api.post("/api/projects", { name: "My Project" });
      queryClient.invalidateQueries({ queryKey: ["datasets"] });
      return project;
    },
    staleTime: Infinity,
  });
}
