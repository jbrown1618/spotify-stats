import "./App.css";
import { useData } from "./useData";

function App() {
  const { data, isLoading } = useData({
    artists: [
      "spotify:artist:6YVMFz59CuY7ngCxTxjpxE",
      "spotify:artist:5t5FqBwTcgKTaWmfEbwQY9",
    ],
  });

  return (
    <>
      <h1>Spotify Stats</h1>
      {isLoading || !data ? (
        <span>Loading...</span>
      ) : (
        <div>
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
