import { Button, Checkbox, Modal, Select } from "@mantine/core";
import { IconFilter, IconX } from "@tabler/icons-react";
import { SetStateAction, useEffect, useRef, useState } from "react";

import { ActiveFilters, defaultFilterOptions, FilterOptions } from "./api";
import styles from "./Filters.module.css";
import { useFilterOptions } from "./useApi";
import { useFilters, useSetFilters } from "./useFilters";
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
    <div className={styles.filtersContainer}>
      <Button variant="subtle" size="xs" onClick={() => setDialogOpen(true)}>
        <IconFilter className={styles.filterIcon} />
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
      transitionProps={{ transition: "fade", duration: 200 }}
      removeScrollProps={{ removeScrollBar: false }}
    >
      <div className={styles.dialogContent}>
        <ListeningPeriodFilter {...props} />
        <PlaylistsFilter {...props} />
        <ArtistsFilter {...props} />
        <AlbumsFilter {...props} />
        <LabelsFilter {...props} />
        <GenresFilter {...props} />
        <ProducersFilter {...props} />
        <YearsFilter {...props} />
        <LikedTracksFilter {...props} />

        <Button
          className={styles.applyButton}
          onClick={() => onClose(localFilters)}
        >
          Apply
        </Button>
      </div>
    </Modal>
  );
}

interface FilterProps {
  filters: ActiveFilters;
  onFilterChange: (a: SetStateAction<ActiveFilters>) => void;
  options: NonNullable<FilterOptions>;
}

function setFilterValue<K extends keyof ActiveFilters>(
  filters: ActiveFilters,
  key: K,
  value: ActiveFilters[K] | null | undefined
): ActiveFilters {
  if (value === undefined || value === null || value === false) {
    const nextFilters = { ...filters };
    delete nextFilters[key];
    return nextFilters;
  }

  return {
    ...filters,
    [key]: value,
  };
}

function ListeningPeriodFilter({ filters, onFilterChange }: FilterProps) {
  const options = namedWrappedOptions();

  return (
    <Select
      className={styles.dialogField}
      label="Wrapped"
      clearable
      data={options}
      value={filters.wrapped ?? null}
      onChange={(range) =>
        onFilterChange((filters) =>
          setFilterValue(filters, "wrapped", range)
        )
      }
    />
  );
}

function PlaylistsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <Select
      className={styles.dialogField}
      label="Playlists"
      clearable
      data={Object.values(options.playlists).map(
        ({ playlist_name, playlist_uri }) => {
          return {
            label: playlist_name,
            value: playlist_uri,
          };
        }
      )}
      value={filters.playlists ?? null}
      searchable
      onChange={(playlist) =>
        onFilterChange((filters) =>
          setFilterValue(filters, "playlists", playlist)
        )
      }
    />
  );
}

function ArtistsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <Select
      className={styles.dialogField}
      label="Artists"
      clearable
      data={Object.values(options.artists).map(
        ({ artist_uri, artist_name }) => {
          return {
            label: artist_name,
            value: artist_uri,
          };
        }
      )}
      value={filters.artists ?? null}
      searchable
      onChange={(artist) =>
        onFilterChange((filters) =>
          setFilterValue(filters, "artists", artist)
        )
      }
    />
  );
}

function AlbumsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <Select
      className={styles.dialogField}
      label="Albums"
      clearable
      data={Object.values(options.albums).map(({ album_uri, album_name }) => {
        return {
          label: album_name,
          value: album_uri,
        };
      })}
      value={filters.albums ?? null}
      searchable
      onChange={(album) =>
        onFilterChange((filters) =>
          setFilterValue(filters, "albums", album)
        )
      }
    />
  );
}

function LabelsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <Select
      className={styles.dialogField}
      label="Labels"
      clearable
      data={Object.values(options.labels).map((album_standardized_label) => {
        return {
          label: album_standardized_label,
          value: album_standardized_label,
        };
      })}
      value={filters.labels ?? null}
      searchable
      onChange={(label) =>
        onFilterChange((filters) =>
          setFilterValue(filters, "labels", label)
        )
      }
    />
  );
}
function GenresFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <Select
      className={styles.dialogField}
      label="Genres"
      clearable
      data={Object.values(options.genres).map((genre) => {
        return {
          label: genre,
          value: genre,
        };
      })}
      value={filters.genres ?? null}
      searchable
      onChange={(genre) =>
        onFilterChange((filters) =>
          setFilterValue(filters, "genres", genre)
        )
      }
    />
  );
}

function YearsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <Select
      className={styles.dialogField}
      label="Release years"
      clearable
      data={Object.values(options.years)
        .sort()
        .reverse()
        .map((year) => {
          return {
            label: "" + year,
            value: "" + year,
          };
        })}
      value={filters.years?.toString() ?? null}
      searchable
      onChange={(year) =>
        onFilterChange((filters) =>
          setFilterValue(
            filters,
            "years",
            year === null ? null : parseInt(year)
          )
        )
      }
    />
  );
}

function LikedTracksFilter({ filters, onFilterChange }: FilterProps) {
  return (
    <Checkbox
      className={styles.dialogField}
      label="Liked"
      checked={filters.liked ?? false}
      onChange={(e) =>
        onFilterChange((filters) =>
          setFilterValue(filters, "liked", e.currentTarget.checked)
        )
      }
    />
  );
}

function ProducersFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <Select
      className={styles.dialogField}
      label="Producers"
      clearable
      data={Object.values(options.producers).map(
        ({ producer_mbid, producer_name }) => {
          return {
            label: producer_name,
            value: producer_mbid,
          };
        }
      )}
      value={filters.producers ?? null}
      searchable
      onChange={(producer) =>
        onFilterChange((filters) =>
          setFilterValue(filters, "producers", producer)
        )
      }
    />
  );
}
