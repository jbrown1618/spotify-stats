import { useState } from "react";
import { ActiveFilters } from "./api";
import "./App.css";
import { Header } from "./Header/Header";
import { useData } from "./useData";
import { Filters } from "./Filters/Filters";

function App() {
  const [filters, setFilters] = useState<ActiveFilters>({});
  const { data, isLoading } = useData(filters);

  return (
    <>
      <Header />
      {isLoading || !data ? (
        <span>Loading...</span>
      ) : (
        <div>
          <Filters
            filters={filters}
            options={data.filter_options}
            onFilterChange={setFilters}
          />
          <h2>Artists</h2>
          {data.artists.map((artist) => (
            <div>{artist.artist_name}</div>
          ))}

          <h2>Tracks</h2>
          {data.tracks.map((track) => (
            <div>{track.track_name}</div>
          ))}
        </div>
      )}
    </>
  );
}

export default App;
