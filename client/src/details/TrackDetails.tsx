import { Text } from "@mantine/core";
import { IconHeart, IconHeartFilled } from "@tabler/icons-react";
import { Fragment } from "react/jsx-runtime";

import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { KPIsList } from "../design/KPI";
import { RowSkeleton } from "../design/RowDesign";
import { TextSkeleton } from "../design/TextSkeleton";
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
      <div style={{ display: "flex", justifyContent: "center" }}>
        <KPIsList
          items={[
            { label: "Album", value: <Text>{track.album_short_name}</Text> },
            {
              label: track.artist_names.length > 1 ? "Artists" : "Artist",
              value: (
                <>
                  {Object.values(track.artist_names).map((artist_name, i) => {
                    return (
                      <Fragment key={artist_name}>
                        <Text>{artist_name}</Text>
                        {i < Object.values(track.artist_names).length - 1 ? (
                          <Text>,&nbsp;</Text>
                        ) : null}
                      </Fragment>
                    );
                  })}
                </>
              ),
            },
            { label: "Streams", value: track.track_stream_count ?? 0 },
            { label: "Popularity", value: track.track_popularity },
            {
              label: "Liked",
              value: track.track_liked ? (
                <IconHeartFilled
                  title="Liked"
                  style={{ color: "green", marginTop: 4 }}
                />
              ) : (
                <IconHeart
                  title="Liked"
                  style={{ color: "gray", marginTop: 4 }}
                />
              ),
            },
          ]}
        />
      </div>
      <TracksStreamingHistoryStack />
      <TrackStreamsLineChart height={300} />
    </>
  );
}
