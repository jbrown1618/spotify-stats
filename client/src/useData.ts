import { useQuery } from "@tanstack/react-query";
import { ActiveFilters, filtersQuery, getData } from "./api";

export function useData(filters: ActiveFilters) {
  const query = filtersQuery(filters);
  return useQuery({
    queryKey: ["data", query],
    queryFn: async () => getData(query),
  });
}
