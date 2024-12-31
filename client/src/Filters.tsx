import { ActiveFilters, defaultFilterOptions, FilterOptions } from "./api";
import {
  Button,
  Checkbox,
  Grid,
  GridCol,
  Modal,
  MultiSelect,
} from "@mantine/core";
import { useSetFilters } from "./useFilters";
import { useIsMobile } from "./useIsMobile";
import { SetStateAction, useEffect, useRef, useState } from "react";

interface FiltersProps {
  filters: ActiveFilters;
  options?: FilterOptions;
}

export function Filters({ filters, options }: FiltersProps) {
  const setFilters = useSetFilters();
  const isMobile = useIsMobile();
  const [dialogOpen, setDialogOpen] = useState(false);

  const lastOptionsRef = useRef(options ?? defaultFilterOptions);
  if (options) {
    lastOptionsRef.current = options;
  }

  const lastOptions = lastOptionsRef.current;

  if (isMobile)
    return (
      <>
        <Button variant="filled" onClick={() => setDialogOpen(true)}>
          Filters
        </Button>
        <FiltersDialog
          filters={filters}
          options={lastOptions}
          opened={dialogOpen}
          onClose={(filters) => {
            setFilters(filters);
            setDialogOpen(false);
          }}
        />
      </>
    );

  return (
    <>
      <h2>Filters</h2>
      <Grid>
        <GridCol span={4}>
          <PlaylistsFilter
            filters={filters}
            options={lastOptions}
            onFilterChange={setFilters}
          />
        </GridCol>

        <GridCol span={4}>
          <ArtistsFilter
            filters={filters}
            options={lastOptions}
            onFilterChange={setFilters}
          />
        </GridCol>

        <GridCol span={4}>
          <AlbumsFilter
            filters={filters}
            options={lastOptions}
            onFilterChange={setFilters}
          />
        </GridCol>

        <GridCol span={4}>
          <LabelsFilter
            filters={filters}
            options={lastOptions}
            onFilterChange={setFilters}
          />
        </GridCol>

        <GridCol span={4}>
          <GenresFilter
            filters={filters}
            options={lastOptions}
            onFilterChange={setFilters}
          />
        </GridCol>

        <GridCol span={4}>
          <YearsFilter
            filters={filters}
            options={lastOptions}
            onFilterChange={setFilters}
          />
        </GridCol>

        <GridCol span={4}>
          <LikedTracksFilter
            filters={filters}
            options={lastOptions}
            onFilterChange={setFilters}
          />
        </GridCol>
      </Grid>
    </>
  );
}

interface FiltersDialogProps extends FiltersProps {
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

  useEffect(() => (opened ? setLocalFilters(filters) : undefined), [opened]);

  return (
    <Modal
      title="Filters"
      opened={opened}
      onClose={() => onClose(localFilters)}
      size="90vw"
      transitionProps={{ transition: "fade", duration: 200 }}
      removeScrollProps={{ removeScrollBar: false }}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <PlaylistsFilter
          filters={localFilters}
          options={options}
          onFilterChange={setLocalFilters}
        />

        <ArtistsFilter
          filters={localFilters}
          options={options}
          onFilterChange={setLocalFilters}
        />

        <AlbumsFilter
          filters={localFilters}
          options={options}
          onFilterChange={setLocalFilters}
        />

        <LabelsFilter
          filters={localFilters}
          options={options}
          onFilterChange={setLocalFilters}
        />

        <GenresFilter
          filters={localFilters}
          options={options}
          onFilterChange={setLocalFilters}
        />

        <YearsFilter
          filters={localFilters}
          options={options}
          onFilterChange={setLocalFilters}
        />

        <LikedTracksFilter
          filters={localFilters}
          options={options}
          onFilterChange={setLocalFilters}
        />

        <Button onClick={() => onClose(localFilters)}>Apply</Button>
      </div>
    </Modal>
  );
}

interface FilterProps extends FiltersProps {
  onFilterChange: (a: SetStateAction<ActiveFilters>) => void;
  options: NonNullable<FilterOptions>;
}

function PlaylistsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
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
  );
}

function ArtistsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
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
  );
}

function AlbumsFilter({ filters, options, onFilterChange }: FilterProps) {
  return (
    <MultiSelect
      label="Filter albums"
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
      label="Filter labels"
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
      label="Filter genres"
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
      label="Filter years"
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
