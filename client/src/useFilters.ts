import { createContext, SetStateAction, useContext } from "react";

import { ActiveFilters } from "./api";

export const FiltersContext = createContext<{
  setFilters: (a: SetStateAction<ActiveFilters>) => void;
  filters: ActiveFilters;
}>({ setFilters: () => {}, filters: {} });

export function useFilters() {
  return useContext(FiltersContext).filters;
}

export function useSetFilters() {
  return useContext(FiltersContext).setFilters;
}
