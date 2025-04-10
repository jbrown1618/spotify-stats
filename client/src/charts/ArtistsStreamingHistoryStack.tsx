import { Artist } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedArtists } from "../sorting";
import { useArtists, useArtistsStreamsByMonth } from "../useApi";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function ArtistsStreamingHistoryStack() {
  const { data: artists } = useArtists();
  const topArtistURIs = artists
    ? Object.values(artists)
        .sort(mostStreamedArtists)
        .slice(0, 5)
        .map((a) => a.artist_uri)
    : [];
  const { data: history } = useArtistsStreamsByMonth(topArtistURIs);

  if (!artists || !history) return <ChartSkeleton />;

  return (
    <>
      <h3>Artist streams by month</h3>
      <StreamingHistoryStack
        data={history}
        getItem={(key) => artists[key]}
        sortItems={(a, b) => b.artist_stream_count - a.artist_stream_count}
        renderItem={(artist: Artist) => (
          <h4
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              margin: 0,
              whiteSpace: "nowrap",
            }}
          >
            <img height={20} src={artist.artist_image_url} />
            {artist.artist_name}
          </h4>
        )}
      />
    </>
  );
}
