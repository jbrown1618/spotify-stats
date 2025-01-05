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

  const artistsOnTrack = artists_by_track[track.track_uri]
    .map((uri) => artists[uri])
    .filter((a) => !!a);

  return (
    <RowDesign
      src={track.album_image_url}
      itemURI={track.album_uri}
      primaryText={track.track_name}
      secondaryText={track.album_name}
      tertiaryText={
        <div style={{ display: "flex" }}>
          {artistsOnTrack.map((artist, i) => {
            return (
              <>
                <Text c="dimmed">{artist.artist_name}</Text>
                {i < artistsOnTrack.length - 1 ? (
                  <Text c="dimmed">,&nbsp;</Text>
                ) : null}
              </>
            );
          })}
        </div>
      }
      stats={[
        isMobile ? null : { label: "Rank", value: track.track_rank },
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
