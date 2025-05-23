import { ChartSkeleton } from "../design/ChartSkeleton";
import { useAlbums, useAlbumsStreamingHistory } from "../useApi";
import { StreamsLineChart } from "./StreamsLineChart";

export function AlbumStreamsLineChart({ height }: { height?: number }) {
  const { data: albums } = useAlbums();
  const { data: history, shouldRender } = useAlbumsStreamingHistory();

  if (!shouldRender) return null;

  if (!history || !albums) return <ChartSkeleton />;

  return (
    <>
      <h3>Album streams over time</h3>
      <StreamsLineChart
        height={height}
        ranks={history}
        getKey={(r) => r.album_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.album_uri}
        getStreams={(r) => r.album_stream_count}
        getLabel={(k) => albums[k]?.album_short_name}
        getCurrentRank={(k) => albums[k]?.album_stream_count * -1}
        getImageURL={(k) => albums[k]?.album_image_url}
      />
    </>
  );
}
