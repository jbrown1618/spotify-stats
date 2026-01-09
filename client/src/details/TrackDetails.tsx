import { IconHeart, IconHeartFilled } from "@tabler/icons-react";
import clsx from "clsx";

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
import sharedStyles from "../list-items/ListItems.module.css";
import { mostStreamedArtists } from "../sorting";
import { useArtists, useTrack, useTrackCredits } from "../useApi";
import styles from "./Details.module.css";
import trackStyles from "./TrackDetails.module.css";

export function TrackDetails({ trackURI }: { trackURI: string }) {
  const { data: track } = useTrack(trackURI);
  const { data: credits } = useTrackCredits(trackURI);

  if (!track)
    return (
      <>
        <TextSkeleton style="h2" />
        <div className={styles.marginBottom}>
          <RowSkeleton />
        </div>
        <ChartSkeleton />
      </>
    );

  return (
    <>
      <h2>{track.track_name}</h2>
      <div className={styles.centered}>
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
                  className={clsx(sharedStyles.likedIcon, sharedStyles.likedIconGreen)}
                />
              ) : (
                <IconHeart
                  title="Liked"
                  className={clsx(sharedStyles.likedIcon, sharedStyles.likedIconGray)}
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
    <div className={trackStyles.artistPills}>
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
  // Group credits by artist (using artist_mbid as the key)
  const creditsByArtist = credits.reduce((acc, credit) => {
    const artistKey = credit.artist_mbid;
    if (!acc[artistKey]) {
      acc[artistKey] = {
        artist: credit,
        creditTypes: new Set<string>(),
      };
    }
    // Add credit type to the set (automatically handles duplicates)
    acc[artistKey].creditTypes.add(credit.credit_type);
    return acc;
  }, {} as Record<string, { artist: Credit; creditTypes: Set<string> }>);

  // Sort artists by name
  const sortedArtists = Object.values(creditsByArtist).sort((a, b) => {
    const nameA = a.artist.artist_name || a.artist.artist_mb_name;
    const nameB = b.artist.artist_name || b.artist.artist_mb_name;
    return nameA.localeCompare(nameB);
  });

  return (
    <div style={{ marginTop: 32, marginBottom: 32 }}>
      <h3 style={{ marginBottom: 16 }}>Credits</h3>
      <table style={{ 
        width: "100%",
        borderCollapse: "collapse",
      }}>
        <thead>
          <tr style={{ 
            borderBottom: "1px solid var(--mantine-color-default-border)",
            textAlign: "left"
          }}>
            <th style={{ 
              padding: "12px 8px",
              fontWeight: 600,
              fontSize: "0.875rem",
              color: "var(--mantine-color-dimmed)"
            }}>
              Artist
            </th>
            <th style={{ 
              padding: "12px 8px",
              fontWeight: 600,
              fontSize: "0.875rem",
              color: "var(--mantine-color-dimmed)"
            }}>
              Credits
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedArtists.map(({ artist, creditTypes }) => (
            <tr key={artist.artist_mbid} style={{ 
              borderBottom: "1px solid var(--mantine-color-default-border)"
            }}>
              <td style={{ padding: "12px 8px" }}>
                <CreditArtist credit={artist} />
              </td>
              <td style={{ padding: "12px 8px" }}>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {Array.from(creditTypes).map((creditType) => (
                    <div
                      key={creditType}
                      style={{
                        padding: "4px 12px",
                        borderRadius: "16px",
                        backgroundColor: "var(--mantine-color-default-hover)",
                        fontSize: "0.875rem",
                        textTransform: "capitalize",
                      }}
                    >
                      {creditType}
                    </div>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CreditArtist({ credit }: { credit: Credit }) {
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
    return <ArtistPill artist={artist} />;
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
    </div>
  );
}
