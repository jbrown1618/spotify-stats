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
      <div style={{ display: "flex" }}>
        <MultiSelect
          label="Filter playlists"
          data={Object.entries(options.playlists).map(
            ([uri, { playlist_name }]) => {
              return {
                label: playlist_name,
                value: uri,
              };
            }
          )}
          value={filters.playlists}
          searchable
          onChange={(playlists) =>
            onFilterChange((filters) => ({
              ...filters,
              playlists,
            }))
          }
        />
        <MultiSelect
          label="Filter artists"
          data={Object.entries(options.artists).map(
            ([uri, { artist_name }]) => {
              return {
                label: artist_name,
                value: uri,
              };
            }
          )}
          value={filters.artists}
          searchable
          onChange={(artists) =>
            onFilterChange((filters) => ({
              ...filters,
              artists,
            }))
          }
        />
        <MultiSelect
          label="Filter albums"
          data={Object.entries(options.albums).map(([uri, { album_name }]) => {
            return {
              label: album_name,
              value: uri,
            };
          })}
          value={filters.albums}
          searchable
          onChange={(albums) =>
            onFilterChange((filters) => ({
              ...filters,
              albums,
            }))
          }
        />
      </div>
    </>
  );
}
