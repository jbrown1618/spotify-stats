import { ArtistsLineChart } from "../charts/ArtistsLineChart";
import { ArtistTile } from "../list-items/ArtistTile";
import { useSummary } from "../useSummary";

interface ArtistDetailsProps {
  artistURI: string;
}

export function ArtistDetails({ artistURI }: ArtistDetailsProps) {
  const { data: summary } = useSummary();
  const artist = summary?.artists[artistURI];
  if (!artist) return null;

  return (
    <>
      <h2>{artist.artist_name}</h2>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-evenly",
          gap: 16,
        }}
      >
        <div style={{ flexGrow: 0 }}>
          <ArtistTile large artist={artist} />
        </div>
        <div
          style={{ flexGrow: 1, flexShrink: 1, minWidth: 100, maxWidth: 800 }}
        >
          <h3>Rank over time</h3>
          <ArtistsLineChart
            height={300}
            ranks={summary.artist_rank_history.filter(
              (r) => r.artist_uri === artist.artist_uri
            )}
            artists={summary.artists}
          />
        </div>
      </div>
    </>
  );
}
