import { SetStateAction } from "react";
import { ActiveFilters, FilterOptions } from "../api";

interface FiltersProps {
  filters: ActiveFilters;
  options: FilterOptions;
  onFilterChange: (a: SetStateAction<ActiveFilters>) => void;
}

export function Filters({ filters, options, onFilterChange }: FiltersProps) {
  return (
    <>
      <h2>Filters</h2>
      <div>
        {Object.keys(options.artists).map((uri) => (
          <ArtistFilter
            name={options.artists[uri]}
            selected={!!filters.artists?.includes(uri)}
            onClick={() =>
              filters.artists?.includes(uri)
                ? onFilterChange((filters) => ({
                    ...filters,
                    artists: filters.artists?.filter((a) => a !== uri),
                  }))
                : onFilterChange((filters) => ({
                    ...filters,
                    artists: [...(filters.artists ?? []), uri],
                  }))
            }
          />
        ))}
      </div>
    </>
  );
}

function ArtistFilter({
  name,
  selected,
  onClick,
}: {
  name: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button onClick={onClick}>
      {name} {selected && "(selected)"}
    </button>
  );
}
