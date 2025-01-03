import "./global.css";

import { Container, Pill, useMantineTheme } from "@mantine/core";

import { Summary } from "./api";
import { AlbumsLineChart } from "./charts/AlbumsLineChart";
import { ArtistsBarChart } from "./charts/ArtistsBarChart";
import { ArtistsLineChart } from "./charts/ArtistsLineChart";
import { GenresBarChart } from "./charts/GenresBarChart";
import { LabelsBarChart } from "./charts/LabelsBarChart";
import { PlaylistsBarChart } from "./charts/PlaylistsBarChart";
import { TracksLineChart } from "./charts/TracksLineChart";
import { YearsBarChart } from "./charts/YearsBarChart";
import { ChartSkeleton } from "./design/ChartSkeleton";
import { DisplayGrid } from "./design/DisplayGrid";
import { Filters } from "./Filters";
import { Header } from "./Header";
import { AlbumRow } from "./list-items/AlbumRow";
import { AlbumTile } from "./list-items/AlbumTile";
import { ArtistRow } from "./list-items/ArtistRow";
import { ArtistTile } from "./list-items/ArtistTile";
import { PlaylistTile } from "./list-items/PlaylistTile";
import { TrackRow } from "./list-items/TrackRow";
import { useData } from "./useData";
import { useFilters, useSetFilters } from "./useFilters";
import { useIsMobile } from "./useIsMobile";

export function App() {
  const isMobile = useIsMobile();
  const filters = useFilters();
  const setFilters = useSetFilters();
  const { data } = useData(filters);
  const t = useMantineTheme();

  return (
    <>
      <div
        style={{
          width: "100%",
          height: isMobile ? 100 : 170,
          backgroundColor: t.colors.green[9],
          position: "absolute",
          zIndex: -1,
        }}
      ></div>
      <Container size="lg">
        <Header />

        <Filters filters={filters} options={data?.filter_options} />

        <div>
          <h2>Artists</h2>

          <ChartWithFallback
            title="Artist ranking over time"
            data={data}
            shouldRender={(d) => d.artist_rank_history.length > 1}
            renderChart={(d) => (
              <ArtistsLineChart
                ranks={d.artist_rank_history}
                artists={d.artists}
              />
            )}
          />

          <ChartWithFallback
            title="Top artists by liked tracks"
            data={data}
            shouldRender={(d) => Object.keys(d.artist_track_counts).length > 1}
            renderChart={(d) => (
              <ArtistsBarChart counts={Object.values(d.artist_track_counts)} />
            )}
          />

          <DisplayGrid
            items={
              data
                ? Object.values(data.artists).sort(
                    (a, b) =>
                      (a.artist_rank ?? Number.MAX_SAFE_INTEGER) -
                      (b.artist_rank ?? Number.MAX_SAFE_INTEGER)
                  )
                : undefined
            }
            getKey={(artist) => artist.artist_uri}
            renderTile={(artist) => (
              <ArtistTile
                artist={artist}
                album_by_artist={data!.albums_by_artist}
                albums={data!.albums}
              />
            )}
            renderLargeTile={(artist) => (
              <ArtistTile
                large
                artist={artist}
                album_by_artist={data!.albums_by_artist}
                albums={data!.albums}
              />
            )}
            renderRow={(artist) => (
              <ArtistRow
                artist={artist}
                album_by_artist={data!.albums_by_artist}
                albums={data!.albums}
              />
            )}
          />

          <h2>Albums</h2>

          <ChartWithFallback
            title="Album ranking over time"
            data={data}
            shouldRender={(d) => d.album_rank_history.length > 1}
            renderChart={(d) => (
              <AlbumsLineChart ranks={d.album_rank_history} albums={d.albums} />
            )}
          />

          <DisplayGrid
            items={
              data
                ? Object.values(data.albums).sort(
                    (a, b) =>
                      (a.album_rank ?? Number.MAX_SAFE_INTEGER) -
                      (b.album_rank ?? Number.MAX_SAFE_INTEGER)
                  )
                : undefined
            }
            getKey={(album) => album.album_uri}
            renderTile={(album) => <AlbumTile album={album} />}
            renderRow={(album) => (
              <AlbumRow
                album={album}
                artists={data!.artists}
                artists_by_album={data!.artists_by_album}
              />
            )}
          />

          <h2>Tracks</h2>

          <ChartWithFallback
            title="Track ranking over time"
            data={data}
            shouldRender={(d) => d.track_rank_history.length > 1}
            renderChart={(d) => (
              <TracksLineChart ranks={d.track_rank_history} tracks={d.tracks} />
            )}
          />

          <DisplayGrid
            items={
              data
                ? Object.values(data.tracks).sort(
                    (a, b) =>
                      (a.track_rank ?? Number.MAX_SAFE_INTEGER) -
                      (b.track_rank ?? Number.MAX_SAFE_INTEGER)
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

          <h2>Playlists</h2>

          <ChartWithFallback
            title="Top playlists by liked tracks"
            data={data}
            shouldRender={(d) =>
              Object.keys(d.playlist_track_counts).length > 1
            }
            renderChart={(d) => (
              <PlaylistsBarChart
                counts={Object.values(d.playlist_track_counts)}
              />
            )}
          />

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
          />

          <h2>Record Labels</h2>
          <ChartWithFallback
            title="Top record labels by liked tracks"
            data={data}
            shouldRender={(d) => Object.keys(d.label_track_counts).length > 1}
            renderChart={(d) => (
              <LabelsBarChart counts={Object.values(d.label_track_counts)} />
            )}
          />
          <DisplayGrid
            items={
              data
                ? Object.values(data.label_track_counts).sort(
                    (a, b) =>
                      (b.label_liked_track_count ?? 0) -
                      (a.label_liked_track_count ?? 0)
                  )
                : undefined
            }
            getKey={(ltc) => ltc.label}
            renderPill={(ltc) => (
              <Pill
                bg="gray"
                size="lg"
                style={{ cursor: "pointer" }}
                onClick={() => setFilters({ labels: [ltc.label] })}
              >
                {ltc.label}
              </Pill>
            )}
          />

          <h2>Genres</h2>
          <ChartWithFallback
            title="Top genres by liked tracks"
            data={data}
            shouldRender={(d) => Object.keys(d.genre_track_counts).length > 1}
            renderChart={(d) => (
              <GenresBarChart counts={Object.values(d.genre_track_counts)} />
            )}
          />
          <DisplayGrid
            items={
              data
                ? Object.values(data.genre_track_counts).sort(
                    (a, b) =>
                      (b.genre_liked_track_count ?? 0) -
                      (a.genre_liked_track_count ?? 0)
                  )
                : undefined
            }
            getKey={(gtc) => gtc.genre}
            renderPill={(gtc) => (
              <Pill
                bg="gray"
                size="lg"
                style={{ cursor: "pointer" }}
                onClick={() => setFilters({ genres: [gtc.genre] })}
              >
                {gtc.genre}
              </Pill>
            )}
          />

          <h2>Release Years</h2>

          <ChartWithFallback
            title="Liked tracks by release year"
            data={data}
            shouldRender={(d) => Object.keys(d.years).length > 1}
            renderChart={(d) => (
              <YearsBarChart counts={Object.values(d.years)} />
            )}
          />
        </div>
      </Container>
    </>
  );
}

interface ChartWithFallbackProps {
  data: Summary | undefined;
  title: string;
  shouldRender: (data: Summary) => boolean;
  renderChart: (data: Summary) => JSX.Element;
}
function ChartWithFallback({
  title,
  data,
  shouldRender,
  renderChart,
}: ChartWithFallbackProps) {
  if (!data)
    return (
      <>
        <h3>{title}</h3>
        <ChartSkeleton />
      </>
    );

  if (!shouldRender(data)) return null;

  return (
    <>
      <h3>{title}</h3>
      {renderChart(data)}
    </>
  );
}
