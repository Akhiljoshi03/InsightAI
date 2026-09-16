import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";

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
