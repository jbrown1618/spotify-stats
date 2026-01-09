import { IconHeart, IconHeartFilled } from "@tabler/icons-react";

import type { Credit } from "../api";
import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { ChartSkeleton } from "../design/ChartSkeleton";
import { KPIsList } from "../design/KPI";
import { PillSkeleton } from "../design/PillDesign";
import { RowSkeleton } from "../design/RowDesign";
import { TextSkeleton } from "../design/TextSkeleton";
import { AlbumPill } from "../list-items/AlbumPill";
import { ArtistPill } from "../list-items/ArtistPill";
import { mostStreamedArtists } from "../sorting";
import { useArtists, useTrack, useTrackCredits } from "../useApi";
import styles from "./TrackDetails.module.css";

export function TrackDetails({ trackURI }: { trackURI: string }) {
  const { data: track } = useTrack(trackURI);
  const { data: credits } = useTrackCredits(trackURI);

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
      {credits && credits.length > 0 && <Credits credits={credits} />}
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
        .sort(mostStreamedArtists)
        .map((artist) => (
          <ArtistPill key={artist.artist_uri} artist={artist} />
        ))}
    </div>
  );
}

function Credits({ credits }: { credits: Credit[] }) {
  // Group credits by type
  const creditsByType = credits.reduce((acc, credit) => {
    if (!acc[credit.credit_type]) {
      acc[credit.credit_type] = [];
    }
    acc[credit.credit_type].push(credit);
    return acc;
  }, {} as Record<string, Credit[]>);

  return (
    <div style={{ marginTop: 32, marginBottom: 32 }}>
      <h3 style={{ marginBottom: 16 }}>Credits</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {Object.entries(creditsByType).map(([creditType, creditsForType]) => (
          <div key={creditType}>
            <h4 style={{ 
              textTransform: "capitalize", 
              marginBottom: 8,
              fontSize: "0.9rem",
              fontWeight: 600,
              color: "var(--mantine-color-dimmed)"
            }}>
              {creditType}
            </h4>
            <div style={{ 
              display: "flex", 
              flexWrap: "wrap", 
              gap: 8,
              marginLeft: 16
            }}>
              {creditsForType.map((credit) => (
                <CreditItem key={`${credit.artist_mbid}-${credit.credit_type}`} credit={credit} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CreditItem({ credit }: { credit: Credit }) {
  // If we have a Spotify artist URI, show it as an ArtistPill
  if (credit.artist_uri && credit.artist_name) {
    const artist = {
      artist_uri: credit.artist_uri,
      artist_name: credit.artist_name,
      artist_image_url: credit.artist_image_url || "",
      artist_followers: 0,
      artist_liked_track_count: 0,
      artist_popularity: 0,
      artist_track_count: 0,
      artist_stream_count: 0,
    };
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        <ArtistPill artist={artist} />
        {credit.credit_details && (
          <span style={{ fontSize: "0.875rem", color: "var(--mantine-color-dimmed)" }}>
            ({credit.credit_details})
          </span>
        )}
      </div>
    );
  }

  // Otherwise, show as plain text
  return (
    <div
      style={{
        padding: "4px 12px",
        borderRadius: "16px",
        backgroundColor: "var(--mantine-color-default-hover)",
        fontSize: "0.875rem",
      }}
    >
      {credit.artist_name || credit.artist_mb_name}
      {credit.credit_details && ` (${credit.credit_details})`}
    </div>
  );
}
