import { Artist } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedArtists } from "../sorting";
import { useArtists, useArtistsStreamsByMonth } from "../useApi";
import { useFilters } from "../useFilters";
import { countUniqueMonths } from "../utils";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function ArtistsStreamingHistoryStack() {
  const filters = useFilters();
  const { data: artists } = useArtists();
  const topArtistURIs = artists
    ? Object.values(artists)
        .filter(
          (a) =>
            filters.artists?.length != 1 || a.artist_uri === filters.artists[0]
        )
        .sort(mostStreamedArtists)
        .slice(0, 5)
        .map((a) => a.artist_uri)
    : [];
  const { data: history } = useArtistsStreamsByMonth(topArtistURIs);

  if (!artists || !history) return <ChartSkeleton />;

  if (countUniqueMonths(history) < 3) return null;

  return (
    <>
      <h3>Artist streams by month</h3>
      <StreamingHistoryStack
        data={history}
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
