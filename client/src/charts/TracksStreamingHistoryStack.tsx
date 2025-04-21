import { Track } from "../api";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedTracks } from "../sorting";
import { useTracks, useTracksStreamsByMonth } from "../useApi";
import { countUniqueMonths } from "../utils";
import { StreamingHistoryStack } from "./StreamingHistoryStack";

export function TracksStreamingHistoryStack() {
  const { data: tracks } = useTracks();
  const topFiveUris = Object.values(tracks ?? {})
    .sort(mostStreamedTracks)
    .slice(0, 5)
    .map((t) => t.track_uri);
  const { data: streamsByMonth } = useTracksStreamsByMonth(topFiveUris);

  if (!tracks || !streamsByMonth) return <ChartSkeleton />;

  if (countUniqueMonths(streamsByMonth) < 3) return null;

  return (
    <>
      <h3>Track streams by month</h3>
      <StreamingHistoryStack
        data={streamsByMonth}
        getItem={(key) => tracks[key]}
        sortItems={mostStreamedTracks}
        renderItem={(track: Track) => (
          <h4
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              margin: 0,
              whiteSpace: "nowrap",
            }}
          >
            <img height={20} src={track.album_image_url} />
            {track.track_name}
          </h4>
        )}
      />
    </>
  );
}
