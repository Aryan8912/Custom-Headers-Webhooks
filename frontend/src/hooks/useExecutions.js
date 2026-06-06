import { useQuery } from "@tanstack/react-query";
import { executionsApi } from "../services/api";

// ── Fetch all executions (paginated + filtered) ────────
export const useExecutions = ({ page = 1, pageSize = 20, agentId, status } = {}) => {
  return useQuery({
    queryKey: ["executions", page, pageSize, agentId, status],
    queryFn: () => executionsApi.getAll({ page, pageSize, agentId, status }),
    refetchInterval: 10000,
    staleTime: 5000,
  });
};

// ── Fetch single execution by ID ───────────────────────
export const useExecution = (executionId) => {
  return useQuery({
    queryKey: ["execution", executionId],
    queryFn: () => executionsApi.getById(executionId),
    enabled: !!executionId,
  });
};