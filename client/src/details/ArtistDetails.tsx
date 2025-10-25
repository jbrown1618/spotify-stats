import { Skeleton } from "@mantine/core";

import { ArtistStreamsLineChart } from "../charts/ArtistsLineChart";
import { ArtistsStreamingHistoryStack } from "../charts/ArtistsStreamingHistoryStack";
import { KPIsList } from "../design/KPI";
import { useAlbums, useArtists } from "../useApi";

interface ArtistDetailsProps {
  artistURI: string;
}

export function ArtistDetails({ artistURI }: ArtistDetailsProps) {
  const { data: artists } = useArtists({ artists: [artistURI] });
  const artist = artists?.[artistURI];

  const { data: artistAlbums } = useAlbums({
    artists: artist ? [artist.artist_uri] : ["NO-ARTIST"],
  });

  if (!artist) return null;

  return (
    <>
      <h2>{artist.artist_name}</h2>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <img
          src={artist.artist_image_url}
          style={{
            height: 200,
            width: 200,
            borderRadius: 100,
            margin: 16,
          }}
        />
        <KPIsList
          items={[
            { label: "Streams", value: artist.artist_stream_count ?? 0 },
            { label: "Popularity", value: artist.artist_popularity },
            {
              label: "Liked Tracks",
              value: `${artist.artist_liked_track_count} / ${artist.artist_track_count}`,
            },
            {
              label: "Albums",
              value: artistAlbums ? (
                Object.keys(artistAlbums).length
              ) : (
                <Skeleton height={24} width={24} />
              ),
            },
          ]}
        />
      </div>

      <ArtistsStreamingHistoryStack onlyArtist={artistURI} />
      <ArtistStreamsLineChart height={300} onlyArtist={artistURI} />
    </>
  );
}
