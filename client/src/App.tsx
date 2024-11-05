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
          {Object.entries(data.artists)
            .slice(0, 50)
            .map(([uri, artist]) => (
              <div key={uri}>{artist.artist_name}</div>
            ))}

          <h2>Tracks</h2>
          {Object.entries(data.tracks)
            .slice(0, 50)
            .map(([uri, track]) => (
              <div key={uri}>{track.track_name}</div>
            ))}
        </div>
      )}
    </>
  );
}

export default App;
