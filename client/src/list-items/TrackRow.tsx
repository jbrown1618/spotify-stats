import { Text } from "@mantine/core";
import { IconHeart, IconHeartFilled } from "@tabler/icons-react";

import { Artist, Track } from "../api";
import { RowDesign } from "../design/RowDesign";
import { useIsMobile } from "../useIsMobile";

interface TrackRowProps {
  track: Track;
  artists_by_track: Record<string, string[]>;
  artists: Record<string, Artist>;
}

export function TrackRow({ track, artists_by_track, artists }: TrackRowProps) {
  const isMobile = useIsMobile();
  return (
    <RowDesign
      src={track.album_image_url}
      primaryText={track.track_name}
      secondaryText={track.album_name}
      tertiaryText={
        <>
          {artists_by_track[track.track_uri].map((artistURI) => {
            const artist = artists[artistURI];
            if (!artist) return null;

            return <Text c="dimmed">{artist.artist_name}</Text>;
          })}
        </>
      }
      stats={[
        { label: "Rank", value: track.track_rank },
        { label: "Streams", value: track.track_stream_count },
        isMobile
          ? null
          : { label: "Popularity", value: track.track_popularity },
        {
          label: "Liked",
          value: track.track_liked ? (
            <IconHeartFilled
              title="Liked"
              style={{ color: "green", marginTop: 4 }}
            />
          ) : (
            <IconHeart
              title="Unliked"
              style={{ color: "gray", marginTop: 4 }}
            />
          ),
        },
      ]}
    />
  );
}
