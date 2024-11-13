import { createContext, SetStateAction, useContext } from "react";
import { ActiveFilters } from "./api";

const SetFiltersContext = createContext<
  (a: SetStateAction<ActiveFilters>) => void
>(() => {});

export const SetFiltersProvider = SetFiltersContext.Provider;

export function useSetFilters() {
  return useContext(SetFiltersContext);
}
