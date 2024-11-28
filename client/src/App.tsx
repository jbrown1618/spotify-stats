import { useState } from "react";
import { ActiveFilters, defaultFilterOptions } from "./api";
import { Header } from "./Header";
import { useData } from "./useData";
import { Filters } from "./Filters";
import "./global.css";
import { PlaylistTile } from "./PlaylistTile";
import { Container, Grid, GridCol, Pill, useMantineTheme } from "@mantine/core";
import { ArtistTile } from "./ArtistTile";
import { AlbumTile } from "./AlbumTile";
import { DisplayGrid } from "./DisplayGrid";
import { SetFiltersProvider } from "./useSetFilters";
import { TracksLineChart } from "./TracksLineChart";
import { PlaylistsBarChart } from "./PlaylistsBarChart";
import { ArtistsLineChart } from "./ArtistsLineChart";
import { AlbumsLineChart } from "./AlbumsLineChart";
import { YearsBarChart } from "./YearsBarChart";
import { ArtistsBarChart } from "./ArtistsBarChart";
import { TrackRow } from "./TrackRow";

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

          {data && (
            <>
              <h3>Top Playlists by Liked Tracks</h3>
              <PlaylistsBarChart
                counts={Object.values(data.playlist_track_counts)}
              />
            </>
          )}

          <DisplayGrid
            items={
              data
                ? Object.values(data.playlists).sort(
                    (a, b) =>
                      b.playlist_liked_track_count -
                      a.playlist_liked_track_count
                  )
                : undefined
            }
            getKey={(playlist) => playlist.playlist_uri}
            renderTile={(playlist) => <PlaylistTile playlist={playlist} />}
            renderRow={(playlist) => <div>{playlist.playlist_name}</div>}
          />

          <h2>Artists</h2>

          {data && (
            <ArtistsLineChart
              ranks={data.artist_rank_history}
              artists={data.artists}
            />
          )}

          {data && (
            <ArtistsBarChart counts={Object.values(data.artist_track_counts)} />
          )}

          <DisplayGrid
            items={
              data
                ? Object.values(data.artists).sort(
                    (a, b) => a.artist_rank - b.artist_rank
                  )
                : undefined
            }
            getKey={(artist) => artist.artist_uri}
            renderTile={(artist) => <ArtistTile artist={artist} />}
            renderRow={(artist) => <div>{artist.artist_name}</div>}
          />

          <h2>Albums</h2>

          {data && (
            <AlbumsLineChart
              ranks={data.album_rank_history}
              albums={data.albums}
            />
          )}

          <DisplayGrid
            items={
              data
                ? Object.values(data.albums).sort(
                    (a, b) => a.album_rank - b.album_rank
                  )
                : undefined
            }
            getKey={(album) => album.album_uri}
            renderTile={(album) => <AlbumTile album={album} />}
            renderRow={(album) => <div>{album.album_name}</div>}
          />

          <h2>Tracks</h2>

          {data && (
            <TracksLineChart
              ranks={data.track_rank_history}
              tracks={data.tracks}
            />
          )}

          <DisplayGrid
            items={
              data
                ? Object.values(data.tracks).sort(
                    (a, b) => a.track_rank - b.track_rank
                  )
                : undefined
            }
            getKey={(track) => track.track_uri}
            renderRow={(track) => (
              <TrackRow
                track={track}
                artists_by_track={data!.artists_by_track}
                artists={data!.artists}
              />
            )}
          />

          <h2>Labels</h2>
          <DisplayGrid
            items={data ? data.labels.sort() : undefined}
            getKey={(label) => label}
            renderPill={(label) => (
              <Pill
                bg="gray"
                size="lg"
                style={{ cursor: "pointer" }}
                onClick={() =>
                  setFilters((filters) => ({ ...filters, labels: [label] }))
                }
              >
                {label}
              </Pill>
            )}
          />

          <h2>Genres</h2>
          <DisplayGrid
            items={data ? data.genres.sort() : undefined}
            getKey={(genre) => genre}
            renderPill={(genre) => (
              <Pill
                bg="gray"
                size="lg"
                style={{ cursor: "pointer" }}
                onClick={() =>
                  setFilters((filters) => ({ ...filters, genres: [genre] }))
                }
              >
                {genre}
              </Pill>
            )}
          />

          <h2>Years</h2>
          {data && <YearsBarChart counts={Object.values(data.years)} />}
        </div>
      </Container>
    </SetFiltersProvider>
  );
}
