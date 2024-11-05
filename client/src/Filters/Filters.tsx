import { SetStateAction } from "react";
import { ActiveFilters, FilterOptions } from "../api";
import { MultiSelect } from "@mantine/core";

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
        <MultiSelect
          label="Filter artists"
          data={Object.entries(options.artists).map(([uri, name]) => ({
            label: name,
            value: uri,
          }))}
          value={filters.artists}
          renderOption={(d) => options.artists[d.option.value]}
          searchable
          onChange={(artists) =>
            onFilterChange((filters) => ({
              ...filters,
              artists,
            }))
          }
        />
      </div>
    </>
  );
}
