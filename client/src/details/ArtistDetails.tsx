import { ArtistsRankLineChart } from "../charts/ArtistsLineChart";
import { ArtistTile } from "../list-items/ArtistTile";
import { useArtists } from "../useApi";
import { useIsMobile } from "../useIsMobile";

interface ArtistDetailsProps {
  artistURI: string;
}

export function ArtistDetails({ artistURI }: ArtistDetailsProps) {
  const { data: artists } = useArtists({ artists: [artistURI] });
  const isMobile = useIsMobile();
  if (!artists) return null;

  const artist = artists[artistURI];
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
          <ArtistsRankLineChart height={300} />
        </div>
      </div>
    </>
  );
}
