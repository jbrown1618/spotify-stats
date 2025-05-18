import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { RowSkeleton } from "../design/RowDesign";
import { TextSkeleton } from "../design/TextSkeleton";
import { TrackRow } from "../list-items/TrackRow";
import { useTrack } from "../useApi";

export function TrackDetails({ trackURI }: { trackURI: string }) {
  const { data: track } = useTrack(trackURI);

  if (!track)
    return (
      <>
        <TextSkeleton style="h2" />
        <div style={{ marginBottom: 16 }}>
          <RowSkeleton />
        </div>
        <ChartSkeleton />
      </>
    );

  return (
    <>
      <h2>{track.track_name}</h2>
      <TrackRow trackUri={trackURI} />
      <TracksStreamingHistoryStack />
      <TrackStreamsLineChart height={300} />
    </>
  );
}
