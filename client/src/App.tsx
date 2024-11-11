import { useState } from "react";
import { ActiveFilters } from "./api";
import { Header } from "./Header/Header";
import { useData } from "./useData";
import { Filters } from "./Filters/Filters";

function App() {
  const [filters, setFilters] = useState<ActiveFilters>({});
  const { data, isLoading } = useData(filters);

  return (
    <>
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
          {Object.values(data.playlists)
            .slice(0, 50)
            .map((playlist) => (
              <div key={playlist.playlist_uri}>{playlist.playlist_name}</div>
            ))}

          <h2>Artists</h2>
          {Object.values(data.artists)
            .slice(0, 50)
            .map((artist) => (
              <div key={artist.artist_uri}>{artist.artist_name}</div>
            ))}

          <h2>Albums</h2>
          {Object.values(data.albums)
            .slice(0, 50)
            .map((album) => (
              <div key={album.album_uri}>{album.album_name}</div>
            ))}

          <h2>Tracks</h2>
          {Object.values(data.tracks)
            .slice(0, 50)
            .map((track) => (
              <div key={track.track_uri}>{track.track_name}</div>
            ))}

          <h2>Labels</h2>
          {Object.values(data.labels)
            .slice(0, 50)
            .map((label) => (
              <div key={label.album_standardized_label}>
                {label.album_standardized_label}
              </div>
            ))}
        </div>
      )}
    </>
  );
}

export default App;
