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
          <h2>Artists</h2>
          {data.artists.map((artist) => (
            <div key={artist.artist_uri}>{artist.artist_name}</div>
          ))}

          <h2>Tracks</h2>
          {data.tracks.map((track) => (
            <div key={track.track_uri}>{track.track_name}</div>
          ))}
        </div>
      )}
    </>
  );
}

export default App;
