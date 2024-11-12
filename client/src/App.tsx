import { useState } from "react";
import { ActiveFilters } from "./api";
import { Header } from "./Header/Header";
import { useData } from "./useData";
import { Filters } from "./Filters/Filters";
import "./global.css";
import { PlaylistTile } from "./Playlists/PlaylistTile";
import { Container } from "@mantine/core";
import { ArtistTile } from "./Artists/ArtistTile";
import { AlbumTile } from "./Albums/AlbumTile";
import { DisplayGrid } from "./DisplayGrid";

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
          <DisplayGrid
            items={Object.values(data.playlists).sort(
              (a, b) =>
                b.playlist_track_liked_count - a.playlist_track_liked_count
            )}
            loading={isLoading}
            getKey={(p) => p.playlist_uri}
            renderTile={(p) => <PlaylistTile playlist={p} />}
            renderRow={(p) => <div>{p.playlist_name}</div>}
          />

          <h2>Artists</h2>
          <DisplayGrid
            items={Object.values(data.artists).sort(
              (a, b) => a.artist_rank - b.artist_rank
            )}
            loading={isLoading}
            getKey={(p) => p.artist_uri}
            renderTile={(p) => <ArtistTile artist={p} />}
            renderRow={(p) => <div>{p.artist_name}</div>}
          />

          <h2>Albums</h2>
          <DisplayGrid
            items={Object.values(data.albums).sort(
              (a, b) => a.album_rank - b.album_rank
            )}
            loading={isLoading}
            getKey={(p) => p.album_uri}
            renderTile={(p) => <AlbumTile album={p} />}
            renderRow={(p) => <div>{p.album_name}</div>}
          />

          <h2>Tracks</h2>
          <DisplayGrid
            items={Object.values(data.tracks).sort(
              (a, b) => a.track_rank - b.track_rank
            )}
            loading={isLoading}
            getKey={(p) => p.track_uri}
            renderRow={(p) => <div>{p.track_name}</div>}
          />

          <h2>Labels</h2>
          <DisplayGrid
            items={data.labels.sort()}
            loading={isLoading}
            getKey={(p) => p}
            renderRow={(p) => <div>{p}</div>}
          />

          <h2>Genres</h2>
          <DisplayGrid
            items={data.genres.sort()}
            loading={isLoading}
            getKey={(p) => p}
            renderRow={(p) => <div>{p}</div>}
          />
        </div>
      )}
    </Container>
  );
}

export default App;
