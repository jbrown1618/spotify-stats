import { SetStateAction } from "react";
import { ActiveFilters, FilterOptions } from "../api";
import { Checkbox, MultiSelect } from "@mantine/core";

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
          data={Object.values(options.playlists).map(
            ({ playlist_name, playlist_uri }) => {
              return {
                label: playlist_name,
                value: playlist_uri,
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
          data={Object.values(options.artists).map(
            ({ artist_uri, artist_name }) => {
              return {
                label: artist_name,
                value: artist_uri,
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
          data={Object.values(options.albums).map(
            ({ album_uri, album_name }) => {
              return {
                label: album_name,
                value: album_uri,
              };
            }
          )}
          value={filters.albums}
          searchable
          onChange={(albums) =>
            onFilterChange((filters) => ({
              ...filters,
              albums,
            }))
          }
        />
        <MultiSelect
          label="Filter labels"
          data={Object.values(options.labels).map(
            ({ album_standardized_label }) => {
              return {
                label: album_standardized_label,
                value: album_standardized_label,
              };
            }
          )}
          value={filters.labels}
          searchable
          onChange={(labels) =>
            onFilterChange((filters) => ({
              ...filters,
              labels,
            }))
          }
        />
        <Checkbox
          label="Liked"
          checked={filters.liked}
          onChange={(e) =>
            onFilterChange((filters) => ({
              ...filters,
              liked: e.currentTarget.checked,
            }))
          }
        />
      </div>
    </>
  );
}
