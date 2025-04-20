import { ChartSkeleton } from "../design/ChartSkeleton";
import { mostStreamedAlbums } from "../sorting";
import { useAlbums, useAlbumsStreamingHistory } from "../useApi";
import { useFilters } from "../useFilters";
import { RankLineChart } from "./RankLineChart";
import { StreamsLineChart } from "./StreamsLineChart";

export function AlbumsRankLineChart({ height }: { height?: number }) {
  const filters = useFilters();
  const { data: albums } = useAlbums();
  const topAlbumURIs = albums
    ? Object.values(albums)
        .filter(
          (a) =>
            filters.albums?.length != 1 || a.album_uri === filters.albums[0]
        )
        .sort(mostStreamedAlbums)
        .slice(0, 10)
        .map((a) => a.album_uri)
    : [];
  const { data: history } = useAlbumsStreamingHistory(topAlbumURIs);

  if (!history || !albums) return <ChartSkeleton />;
  return (
    <>
      <h3>Album ranking over time</h3>
      <RankLineChart
        height={height}
        ranks={history}
        getKey={(r) => r.album_uri}
        getDate={(r) => r.as_of_date}
        getItem={(r) => r.album_uri}
        getRank={(r) => r.album_rank}
        getLabel={(k) => albums[k]?.album_short_name}
        getCurrentRank={(k) => albums[k]?.album_stream_count * -1}
        getImageURL={(k) => albums[k]?.album_image_url}
      />
    </>
  );
}

export function AlbumStreamsLineChart({ height }: { height?: number }) {
  const { data: albums } = useAlbums();
  const topAlbumURIs = albums
    ? Object.values(albums)
        .sort(mostStreamedAlbums)
        .slice(0, 10)
        .map((a) => a.album_uri)
    : [];
  const { data: history } = useAlbumsStreamingHistory(topAlbumURIs);

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
