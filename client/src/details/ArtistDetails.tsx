import { ArtistStreamsLineChart } from "../charts/ArtistsLineChart";
import { ArtistsStreamingHistoryStack } from "../charts/ArtistsStreamingHistoryStack";
import { ArtistTile } from "../list-items/ArtistTile";
import { useArtists } from "../useApi";

interface ArtistDetailsProps {
  artistURI: string;
}

export function ArtistDetails({ artistURI }: ArtistDetailsProps) {
  const { data: artists } = useArtists({ artists: [artistURI] });
  if (!artists) return null;

  const artist = artists[artistURI];
  if (!artist) return null;

  return (
    <>
      <h2>{artist.artist_name}</h2>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <ArtistTile large artist={artist} />
      </div>

      <ArtistsStreamingHistoryStack onlyArtist={artistURI} />
      <ArtistStreamsLineChart height={300} onlyArtist={artistURI} />
    </>
  );
}
