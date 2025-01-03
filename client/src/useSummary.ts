import { useQuery } from "@tanstack/react-query";

import { getData, toFiltersQuery } from "./api";
import { useFilters } from "./useFilters";

export function useSummary() {
  const filters = useFilters();
  const query = toFiltersQuery(filters);
  return useQuery({
    queryKey: ["data", query],
    queryFn: async () => getData(query),
    staleTime: 1000 * 60 * 60,
    gcTime: 1000 * 60 * 60,
  });
}
