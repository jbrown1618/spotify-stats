import { useQuery } from "@tanstack/react-query";
import { ActiveFilters, toFiltersQuery, getData } from "./api";

export function useData(filters: ActiveFilters) {
  const query = toFiltersQuery(filters);
  return useQuery({
    queryKey: ["data", query],
    queryFn: async () => getData(query),
  });
}
