import {
  createContext,
  SetStateAction,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { ActiveFilters, fromFiltersQuery, toFiltersQuery } from "./api";

const FiltersContext = createContext<{
  setFilters: (a: SetStateAction<ActiveFilters>) => void;
  filters: ActiveFilters;
}>({ setFilters: () => {}, filters: {} });

FiltersContext.Provider;

export function FiltersProvider({
  children,
}: React.PropsWithChildren<unknown>) {
  const [filters, _setFilters] = useState<ActiveFilters>(
    fromFiltersQuery(window.location.search)
  );
  const setFilters = useCallback((a: SetStateAction<ActiveFilters>) => {
    _setFilters((oldFilters) => {
      const newFilters = typeof a === "function" ? a(oldFilters) : a;

      const query = toFiltersQuery(newFilters);

      window.scrollTo(0, 0);
      const url = query
        ? `${window.location.origin}?${toFiltersQuery(newFilters)}`
        : window.location.origin;
      history.pushState(newFilters, "", url);

      return newFilters;
    });
  }, []);

  useEffect(() => {
    const onBackOrForward = () => {
      _setFilters(fromFiltersQuery(window.location.search));
    };

    window.addEventListener("popstate", onBackOrForward);
    return () => window.removeEventListener("popstate", onBackOrForward);
  }, []);

  return (
    <FiltersContext.Provider value={{ filters, setFilters }}>
      {children}
    </FiltersContext.Provider>
  );
}

export function useFilters() {
  return useContext(FiltersContext).filters;
}

export function useSetFilters() {
  return useContext(FiltersContext).setFilters;
}
