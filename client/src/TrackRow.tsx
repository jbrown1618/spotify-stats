import { Paper, Pill, Text } from "@mantine/core";
import { Artist, Track } from "./api";
import { IconHeartFilled } from "@tabler/icons-react";

interface TrackRowProps {
  track: Track;
  artists_by_track: Record<string, string[]>;
  artists: Record<string, Artist>;
}

export function TrackRow({ track, artists_by_track, artists }: TrackRowProps) {
  return (
    <Paper
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: 4,
      }}
    >
      <div style={{ display: "flex", alignItems: "start", gap: 16 }}>
        <img src={track.album_image_url} style={{ height: 70 }} />
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <Text fw={700}>{track.track_name}</Text>
            {track.track_explicit && <Pill bg="gray">Explicit</Pill>}
          </div>
          <Text>{track.album_name}</Text>
          <span style={{ display: "flex" }}>
            {artists_by_track[track.track_uri].map((artistURI) => {
              const artist = artists[artistURI];
              if (!artist) return null;

              return <Text c="dimmed">{artist.artist_name}</Text>;
            })}
          </span>
        </div>
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "start" }}>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Text c="dimmed">Rank</Text>
          <Text size={"xl"}>{track.track_rank}</Text>
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Text c="dimmed">Liked</Text>
          {track.track_liked}
          <IconHeartFilled style={{ color: "green", marginTop: 4 }} />
        </div>
      </div>
    </Paper>
  );
}
