import { Button, Checkbox, Modal, MultiSelect, Select } from "@mantine/core";
import { IconFilter, IconX } from "@tabler/icons-react";
import { SetStateAction, useEffect, useRef, useState } from "react";

import { ActiveFilters, defaultFilterOptions, FilterOptions } from "./api";
import { useFilterOptions } from "./useApi";
import { useFilters, useSetFilters } from "./useFilters";
import { useIsMobile } from "./useIsMobile";
import { namedWrappedOptions } from "./utils";

export function Filters() {
  const filters = useFilters();
  const { data: options } = useFilterOptions();
  const setFilters = useSetFilters();
  const [dialogOpen, setDialogOpen] = useState(false);

  const lastOptionsRef = useRef(options ?? defaultFilterOptions);
  if (options) {
    lastOptionsRef.current = options;
  }

  const lastOptions = lastOptionsRef.current;

  return (
    <div style={{ display: "flex", flexWrap: "nowrap", alignItems: "center" }}>
      <Button variant="subtle" size="xs" onClick={() => setDialogOpen(true)}>
        <IconFilter style={{ marginRight: 8 }} />
        Filters
      </Button>
      {Object.keys(filters).length > 0 && (
        <Button variant="subtle" size="xs" onClick={() => setFilters({})}>
          <IconX />
        </Button>
      )}
      <FiltersDialog
        filters={filters}
        options={lastOptions}
        opened={dialogOpen}
        onClose={(filters) => {
          setFilters(filters);
          setDialogOpen(false);
        }}
      />
    </div>
  );
}

interface FiltersDialogProps {
  filters: ActiveFilters;
  options: NonNullable<FilterOptions>;
  opened: boolean;
  onClose: (filters: ActiveFilters) => void;
}

function FiltersDialog({
  filters,
  options,
  opened,
  onClose,
}: FiltersDialogProps) {
  const isMobile = useIsMobile();
  const [localFilters, setLocalFilters] = useState(filters);

  useEffect(
    () => (opened ? setLocalFilters(filters) : undefined),
    [opened, filters]
  );

  const props = {
    filters: localFilters,
    options,
    onFilterChange: setLocalFilters,
  };

  return (
    <Modal
      title="Filters"
      opened={opened}
      onClose={() => onClose(localFilters)}
      size={isMobile ? "90vw" : "md"}
      transitionProps={{ transition: "fade", duration: 200 }}
      removeScrollProps={{ removeScrollBar: false }}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <ListeningPeriodFilter {...props} />
        <PlaylistsFilter {...props} />
        <ArtistsFilter {...props} />
        <AlbumsFilter {...props} />
        <LabelsFilter {...props} />
        <GenresFilter {...props} />
        <ProducersFilter {...props} />
        <YearsFilter {...props} />
        <LikedTracksFilter {...props} />

        <Button onClick={() => onClose(localFilters)}>Apply</Button>
      </div>
    </Modal>
  );
}

interface FilterProps {
  filters: ActiveFilters;
  onFilterChange: (a: SetStateAction<ActiveFilters>) => void;
  options: NonNullable<FilterOptions>;
}

function ListeningPeriodFilter({ filters, onFilterChange }: FilterProps) {
  const options = namedWrappedOptions();

  return (
    <Select
      label="Wrapped"
      clearable
      data={options}
      value={filters.wrapped}
      onChange={(range) =>
        onFilterChange((filters) => ({
          ...filters,
          wrapped: range ?? undefined,
        }))
      }
    />
  );
}

function PlaylistsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <MultiSelect
      label="Playlists"
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
  );
}

function ArtistsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <MultiSelect
      label="Artists"
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
  );
}

function AlbumsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <MultiSelect
      label="Albums"
      data={Object.values(options.albums).map(({ album_uri, album_name }) => {
        return {
          label: album_name,
          value: album_uri,
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
  );
}

function LabelsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <MultiSelect
      label="Labels"
      data={Object.values(options.labels).map((album_standardized_label) => {
        return {
          label: album_standardized_label,
          value: album_standardized_label,
        };
      })}
      value={filters.labels}
      searchable
      onChange={(labels) =>
        onFilterChange((filters) => ({
          ...filters,
          labels,
        }))
      }
    />
  );
}
function GenresFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <MultiSelect
      label="Genres"
      data={Object.values(options.genres).map((genre) => {
        return {
          label: genre,
          value: genre,
        };
      })}
      value={filters.genres}
      searchable
      onChange={(genres) =>
        onFilterChange((filters) => ({
          ...filters,
          genres,
        }))
      }
    />
  );
}

function YearsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <MultiSelect
      label="Release years"
      data={Object.values(options.years)
        .sort()
        .reverse()
        .map((year) => {
          return {
            label: "" + year,
            value: "" + year,
          };
        })}
      value={filters.years?.map((y) => "" + y)}
      searchable
      onChange={(years) =>
        onFilterChange((filters) => ({
          ...filters,
          years: years.map((y) => parseInt(y)),
        }))
      }
    />
  );
}

function LikedTracksFilter({ filters, onFilterChange }: FilterProps) {
  return (
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
  );
}

function ProducersFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <MultiSelect
      label="Producers"
      data={Object.values(options.producers).map(
        ({ producer_mbid, producer_name }) => {
          return {
            label: producer_name,
            value: producer_mbid,
          };
        }
      )}
      value={filters.producers}
      searchable
      onChange={(producers) =>
        onFilterChange((filters) => ({
          ...filters,
          producers,
        }))
      }
    />
  );
}
