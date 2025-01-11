import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";

import { fetchWrapped } from "./api";

export function useWrapped() {
  const { year: yearParam } = useParams();
  const year = parseInt(yearParam ?? "");

  return useQuery({
    queryKey: ["wrapped", year],
    queryFn: async () => {
      if (!year || Number.isNaN(year)) return null;
      return fetchWrapped(year);
    },
    staleTime: 1000 * 60 * 60,
    gcTime: 1000 * 60 * 60,
  });
}
