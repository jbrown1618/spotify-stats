import { Artist } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedArtists } from "../sorting";
import { useArtists, useArtistsStreamsByMonth } from "../useApi";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function ArtistsStreamingHistoryStack({
  onlyArtist,
}: {
  onlyArtist?: string;
}) {
  const { data: artists } = useArtists();
  const { data: history, shouldRender } = useArtistsStreamsByMonth();

  if (!artists || !history) return <ChartSkeleton />;

  if (!shouldRender) return null;

  const data = onlyArtist
    ? Object.fromEntries(
        Object.entries(history).filter(
          ([artistUri]) => artistUri === onlyArtist
        )
      )
    : history;

  return (
    <>
      <h3>Artist streams by month</h3>
      <StreamingHistoryStack
        data={data}
        getItem={(key) => artists[key]}
        sortItems={mostStreamedArtists}
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
