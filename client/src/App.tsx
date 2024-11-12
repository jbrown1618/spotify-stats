import { useState } from "react";
import { ActiveFilters } from "./api";
import { Header } from "./Header/Header";
import { useData } from "./useData";
import { Filters } from "./Filters/Filters";
import "./global.css";
import { PlaylistTile } from "./Playlists/PlaylistTile";
import { Container, Grid, GridCol } from "@mantine/core";
import { ArtistTile } from "./Artists/ArtistTile";
import { AlbumTile } from "./Albums/AlbumTile";

const defaultGridCount = 1 * 2 * 3 * 5;
function App() {
  const [filters, setFilters] = useState<ActiveFilters>({});
  const { data, isLoading } = useData(filters);

  return (
    <Container size="lg">
      <Header />
      {data && (
        <Filters
          filters={filters}
          options={data.filter_options}
          onFilterChange={setFilters}
        />
      )}

      {isLoading || !data ? (
        <span>Loading...</span>
      ) : (
        <div>
          <h2>Playlists</h2>
          <Grid>
            {Object.values(data.playlists)
              .sort(
                (a, b) =>
                  b.playlist_track_liked_count - a.playlist_track_liked_count
              )
              .slice(0, defaultGridCount)
              .map((playlist) => (
                <GridCol span={2}>
                  <PlaylistTile
                    key={playlist.playlist_uri}
                    playlist={playlist}
                  />
                </GridCol>
              ))}
          </Grid>

          <h2>Artists</h2>
          <Grid>
            {Object.values(data.artists)
              .sort((a, b) => a.artist_rank - b.artist_rank)
              .slice(0, defaultGridCount)
              .map((artist) => (
                <GridCol span={2}>
                  <ArtistTile key={artist.artist_uri} artist={artist} />
                </GridCol>
              ))}
          </Grid>

          <h2>Albums</h2>
          <Grid>
            {Object.values(data.albums)
              .sort((a, b) => a.album_rank - b.album_rank)
              .slice(0, defaultGridCount)
              .map((album) => (
                <GridCol span={2}>
                  <AlbumTile key={album.album_uri} album={album} />
                </GridCol>
              ))}
          </Grid>

          <h2>Tracks</h2>
          {Object.values(data.tracks)
            .slice(0, defaultGridCount)
            .map((track) => (
              <div key={track.track_uri}>{track.track_name}</div>
            ))}

          <h2>Labels</h2>
          {Object.values(data.labels)
            .slice(0, defaultGridCount)
            .map((label) => (
              <div key={label}>{label}</div>
            ))}

          <h2>Genres</h2>
          {Object.values(data.genres)
            .slice(0, defaultGridCount)
            .map((genre) => (
              <div key={genre}>{genre}</div>
            ))}
        </div>
      )}
    </Container>
  );
}

export default App;
