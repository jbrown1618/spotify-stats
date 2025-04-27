import { useFilters } from "../useFilters";
import { namedWrappedOptions } from "../utils";

export function WrappedDetails() {
  const { wrapped } = useFilters();

  const label =
    namedWrappedOptions().find((o) => o.value === wrapped)?.label ?? wrapped;

  return <h2>Wrapped: {label}</h2>;
}
