import { IconHeart, IconHeartFilled } from "@tabler/icons-react";

import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { KPIsList } from "../design/KPI";
import { PillSkeleton } from "../design/PillDesign";
import { RowSkeleton } from "../design/RowDesign";
import { TextSkeleton } from "../design/TextSkeleton";
import { AlbumPill } from "../list-items/AlbumPill";
import { ArtistPill } from "../list-items/ArtistPill";
import { useArtists, useTrack } from "../useApi";
import styles from "./TrackDetails.module.css";

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
            { label: "Album", value: <AlbumPill album={track} /> },
            {
              label: track.artist_names.length > 1 ? "Artists" : "Artist",
              value: <ArtistPills uris={track.artist_uris} />,
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

function ArtistPills({ uris }: { uris: string[] }) {
  const { data: artists } = useArtists({ artists: uris });
  if (!artists) {
    return <PillSkeleton />;
  }

  return (
    <div className={styles.artistPills}>
      {uris
        .map((uri) => artists[uri])
        .map((artist) => (
          <ArtistPill key={artist.artist_uri} artist={artist} />
        ))}
    </div>
  );
}
