import { ArtistsRankLineChart } from "../charts/ArtistsLineChart";
import { ArtistTile } from "../list-items/ArtistTile";
import { useIsMobile } from "../useIsMobile";
import { useSummary } from "../useApi";

interface ArtistDetailsProps {
  artistURI: string;
}

export function ArtistDetails({ artistURI }: ArtistDetailsProps) {
  const { data: summary } = useSummary();
  const isMobile = useIsMobile();
  const artist = summary?.artists[artistURI];
  if (!artist) return null;

  return (
    <>
      <h2>{artist.artist_name}</h2>
      <div
        style={{
          display: "flex",
          flexDirection: isMobile ? "column" : "row",
          justifyContent: "center",
          gap: 16,
        }}
      >
        <div
          style={{ flexGrow: 0, alignSelf: isMobile ? "center" : undefined }}
        >
          <ArtistTile large artist={artist} />
        </div>
        <div style={{ flexGrow: 1 }}>
          <h3>Rank over time</h3>
          <ArtistsRankLineChart
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
