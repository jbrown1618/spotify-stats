import { useState } from "react";
import { ActiveFilters, defaultFilterOptions } from "./api";
import { Header } from "./Header/Header";
import { useData } from "./useData";
import { Filters } from "./Filters/Filters";
import "./global.css";
import { PlaylistTile } from "./Playlists/PlaylistTile";
import { Container, useMantineTheme } from "@mantine/core";
import { ArtistTile } from "./Artists/ArtistTile";
import { AlbumTile } from "./Albums/AlbumTile";
import { DisplayGrid } from "./DisplayGrid";
import { SetFiltersProvider } from "./useSetFilters";

export function App() {
  const [filters, setFilters] = useState<ActiveFilters>({});
  const { data } = useData(filters);
  const t = useMantineTheme();

  return (
    <SetFiltersProvider value={setFilters}>
      <div
        style={{
          width: "100%",
          height: 170,
          backgroundColor: t.colors.green[9],
          position: "absolute",
          zIndex: -1,
        }}
      ></div>
      <Container size="lg">
        <Header />

        <Filters
          filters={filters}
          options={data?.filter_options ?? defaultFilterOptions}
        />

        <div>
          <h2>Playlists</h2>
          <DisplayGrid
            items={
              data
                ? Object.values(data.playlists).sort(
                    (a, b) =>
                      b.playlist_track_liked_count -
                      a.playlist_track_liked_count
                  )
                : undefined
            }
            getKey={(p) => p.playlist_uri}
            renderTile={(p) => <PlaylistTile playlist={p} />}
            renderRow={(p) => <div>{p.playlist_name}</div>}
          />

          <h2>Artists</h2>
          <DisplayGrid
            items={
              data
                ? Object.values(data.artists).sort(
                    (a, b) => a.artist_rank - b.artist_rank
                  )
                : undefined
            }
            getKey={(p) => p.artist_uri}
            renderTile={(p) => <ArtistTile artist={p} />}
            renderRow={(p) => <div>{p.artist_name}</div>}
          />

          <h2>Albums</h2>
          <DisplayGrid
            items={
              data
                ? Object.values(data.albums).sort(
                    (a, b) => a.album_rank - b.album_rank
                  )
                : undefined
            }
            getKey={(p) => p.album_uri}
            renderTile={(p) => <AlbumTile album={p} />}
            renderRow={(p) => <div>{p.album_name}</div>}
          />

          <h2>Tracks</h2>
          <DisplayGrid
            items={
              data
                ? Object.values(data.tracks).sort(
                    (a, b) => a.track_rank - b.track_rank
                  )
                : undefined
            }
            getKey={(p) => p.track_uri}
            renderRow={(p) => <div>{p.track_name}</div>}
          />

          <h2>Labels</h2>
          <DisplayGrid
            items={data ? data.labels.sort() : undefined}
            getKey={(p) => p}
            renderRow={(p) => <div>{p}</div>}
          />

          <h2>Genres</h2>
          <DisplayGrid
            items={data ? data.genres.sort() : undefined}
            getKey={(p) => p}
            renderRow={(p) => <div>{p}</div>}
          />
        </div>
      </Container>
    </SetFiltersProvider>
  );
}
