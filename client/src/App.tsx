import "./global.css";

import { Anchor, Container, Pill, Tabs, useMantineTheme } from "@mantine/core";

import { Summary } from "./api";
import {
  AlbumsRankLineChart,
  AlbumStreamsLineChart,
} from "./charts/AlbumsLineChart";
import { ArtistsBarChart } from "./charts/ArtistsBarChart";
import {
  ArtistsRankLineChart,
  ArtistStreamsLineChart,
} from "./charts/ArtistsLineChart";
import { GenresBarChart } from "./charts/GenresBarChart";
import { LabelsBarChart } from "./charts/LabelsBarChart";
import { PlaylistsBarChart } from "./charts/PlaylistsBarChart";
import { StreamingHistoryAreaChart } from "./charts/StreamingHistoryAreaChart";
import { StreamingHistoryStack } from "./charts/StreamingHistoryStack";
import {
  TracksRankLineChart,
  TrackStreamsLineChart,
} from "./charts/TracksLineChart";
import { YearsBarChart } from "./charts/YearsBarChart";
import { ChartSkeleton } from "./design/ChartSkeleton";
import { DisplayGrid } from "./design/DisplayGrid";
import { AlbumDetails } from "./details/AlbumDetails";
import { ArtistDetails } from "./details/ArtistDetails";
import { Filters } from "./Filters";
import { AlbumRow } from "./list-items/AlbumRow";
import { AlbumTile } from "./list-items/AlbumTile";
import { ArtistRow } from "./list-items/ArtistRow";
import { ArtistTile } from "./list-items/ArtistTile";
import { PlaylistTile } from "./list-items/PlaylistTile";
import { TrackRow } from "./list-items/TrackRow";
import {
  albumSortOptions,
  artistSortOptions,
  trackSortOptions,
} from "./sorting";
import { useFilters, useSetFilters } from "./useFilters";
import { useIsMobile } from "./useIsMobile";
import { useSummary } from "./useSummary";

export function App() {
  const isMobile = useIsMobile();
  const filters = useFilters();
  const setFilters = useSetFilters();
  const { data } = useSummary();
  const t = useMantineTheme();

  return (
    <>
      <div
        style={{
          width: "100%",
          height: isMobile ? 40 : 170,
          backgroundColor: t.colors.green[9],
          position: "absolute",
          zIndex: -1,
        }}
      ></div>
      <Container size="lg">
        <nav
          style={{
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <h1 style={{ margin: 0, whiteSpace: "nowrap" }}>Spotify Stats</h1>
          {isMobile && (
            <Filters filters={filters} options={data?.filter_options} />
          )}
        </nav>

        {!isMobile && (
          <Filters filters={filters} options={data?.filter_options} />
        )}

        {filters.artists?.length === 1 && (
          <ArtistDetails artistURI={filters.artists[0]} />
        )}

        {filters.albums?.length === 1 && (
          <AlbumDetails albumURI={filters.albums[0]} />
        )}

        <div>
          {filters.artists?.length !== 1 && (
            <>
              <h2>Artists</h2>

              <Tabs defaultValue="rank">
                <Tabs.List>
                  <Tabs.Tab value="rank">Rank</Tabs.Tab>
                  <Tabs.Tab value="streams">Streams</Tabs.Tab>
                  <Tabs.Tab value="count">Count</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="rank">
                  <ChartWithFallback
                    title="Artist ranking over time"
                    data={data}
                    shouldRender={(d) => d.artist_rank_history.length > 1}
                    renderChart={(d) => (
                      <ArtistsRankLineChart
                        ranks={d.artist_rank_history}
                        artists={d.artists}
                      />
                    )}
                  />
                </Tabs.Panel>

                <Tabs.Panel value="streams">
                  <ChartWithFallback
                    title="Artist streams over time"
                    data={data}
                    shouldRender={(d) => d.artist_rank_history.length > 1}
                    renderChart={(d) => (
                      <ArtistStreamsLineChart
                        ranks={d.artist_rank_history}
                        artists={d.artists}
                      />
                    )}
                  />
                </Tabs.Panel>

                <Tabs.Panel value="count">
                  <ChartWithFallback
                    title="Artists by liked tracks"
                    data={data}
                    shouldRender={(d) =>
                      Object.keys(d.artist_track_counts).length > 1
                    }
                    renderChart={(d) => (
                      <ArtistsBarChart
                        counts={Object.values(d.artist_track_counts)}
                      />
                    )}
                  />
                </Tabs.Panel>
              </Tabs>

              <DisplayGrid
                items={data ? Object.values(data.artists) : undefined}
                sortOptions={artistSortOptions}
                getKey={(artist) => artist.artist_uri}
                renderTile={(artist) => <ArtistTile artist={artist} />}
                renderLargeTile={(artist) => (
                  <ArtistTile large artist={artist} />
                )}
                renderRow={(artist) => (
                  <ArtistRow
                    artist={artist}
                    album_by_artist={data!.albums_by_artist}
                    albums={data!.albums}
                  />
                )}
              />
            </>
          )}

          <h2>Tracks</h2>

          <Tabs defaultValue="rank">
            <Tabs.List>
              <Tabs.Tab value="rank">Rank</Tabs.Tab>
              <Tabs.Tab value="streams">Streams</Tabs.Tab>
              <Tabs.Tab value="months">Comparison</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="rank">
              <ChartWithFallback
                title="Track ranking over time"
                data={data}
                shouldRender={(d) => d.track_rank_history.length > 1}
                renderChart={(d) => (
                  <TracksRankLineChart
                    ranks={d.track_rank_history}
                    tracks={d.tracks}
                  />
                )}
              />
            </Tabs.Panel>

            <Tabs.Panel value="streams">
              <ChartWithFallback
                title="Track streams over time"
                data={data}
                shouldRender={(d) => d.track_rank_history.length > 1}
                renderChart={(d) => (
                  <TrackStreamsLineChart
                    ranks={d.track_rank_history}
                    tracks={d.tracks}
                  />
                )}
              />
            </Tabs.Panel>

            <Tabs.Panel value="months">
              <ChartWithFallback
                title="Track streams by month"
                data={data}
                shouldRender={(d) =>
                  Object.keys(d.track_streams_by_month).length > 1
                }
                renderChart={(d) => (
                  <StreamingHistoryStack
                    data={d.track_streams_by_month}
                    renderKey={(key) => (
                      <h4
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                          margin: 0,
                          whiteSpace: "nowrap",
                        }}
                      >
                        <img
                          height={20}
                          src={data!.tracks[key].album_image_url}
                        />
                        {data!.tracks[key].track_name}
                      </h4>
                    )}
                  />
                )}
              />
            </Tabs.Panel>
          </Tabs>

          <DisplayGrid
            items={data ? Object.values(data.tracks) : undefined}
            sortOptions={trackSortOptions}
            getKey={(track) => track.track_uri}
            renderRow={(track) => (
              <TrackRow
                track={track}
                artists_by_track={data!.artists_by_track}
                artists={data!.artists}
              />
            )}
          />

          {filters.albums?.length !== 1 && (
            <>
              <h2>Albums</h2>

              <Tabs defaultValue="rank">
                <Tabs.List>
                  <Tabs.Tab value="rank">Rank</Tabs.Tab>
                  <Tabs.Tab value="streams">Streams</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="rank">
                  <ChartWithFallback
                    title="Album ranking over time"
                    data={data}
                    shouldRender={(d) => d.album_rank_history.length > 1}
                    renderChart={(d) => (
                      <AlbumsRankLineChart
                        ranks={d.album_rank_history}
                        albums={d.albums}
                      />
                    )}
                  />
                </Tabs.Panel>

                <Tabs.Panel value="streams">
                  <ChartWithFallback
                    title="Album streams over time"
                    data={data}
                    shouldRender={(d) => d.album_rank_history.length > 1}
                    renderChart={(d) => (
                      <AlbumStreamsLineChart
                        ranks={d.album_rank_history}
                        albums={d.albums}
                      />
                    )}
                  />
                </Tabs.Panel>
              </Tabs>

              <DisplayGrid
                items={data ? Object.values(data.albums) : undefined}
                sortOptions={albumSortOptions}
                getKey={(album) => album.album_uri}
                renderTile={(album) => <AlbumTile album={album} />}
                renderLargeTile={(album) => <AlbumTile large album={album} />}
                renderRow={(album) => (
                  <AlbumRow
                    album={album}
                    artists={data!.artists}
                    artists_by_album={data!.artists_by_album}
                  />
                )}
              />
            </>
          )}

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

          {(!data || Object.keys(data.years).length > 1) && (
            <>
              <h2>Release Years</h2>

              <ChartWithFallback
                title="Liked tracks by release year"
                data={data}
                shouldRender={(d) => Object.keys(d.years).length > 1}
                renderChart={(d) => (
                  <YearsBarChart counts={Object.values(d.years)} />
                )}
              />
            </>
          )}

          <h2>Streaming history</h2>
          <ChartWithFallback
            title="Streams by month"
            data={data}
            shouldRender={(d) => Object.keys(d.streams_by_month).length > 1}
            renderChart={(d) => (
              <StreamingHistoryAreaChart
                streams_by_month={d.streams_by_month}
              />
            )}
          />
        </div>

        <footer style={{ padding: 16, textAlign: "center" }}>
          <Anchor
            href="https://www.github.com/jbrown1618/spotify-stats"
            target="_blank"
            underline="hover"
          >
            jbrown1618/spotify-stats
          </Anchor>
        </footer>
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
