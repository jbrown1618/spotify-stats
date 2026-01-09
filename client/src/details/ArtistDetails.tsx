import { Pill, Skeleton } from "@mantine/core";

import { ArtistStreamsLineChart } from "../charts/ArtistsLineChart";
import { ArtistsStreamingHistoryStack } from "../charts/ArtistsStreamingHistoryStack";
import { KPIsList } from "../design/KPI";
import { PillWithAvatar } from "../design/PillDesign";
import { ArtistPill } from "../list-items/ArtistPill";
import { useAlbums, useArtistCredits, useArtists } from "../useApi";
import { useSetFilters } from "../useFilters";
import styles from "./Details.module.css";

interface ArtistDetailsProps {
  artistURI: string;
}

// Helper function to format MusicBrainz artist names
// If the name contains only non-latin characters, append the sort name
function formatMBArtistName(
  mbName: string,
  sortName: string | null | undefined
): string {
  // If sortName is not available, just return the name
  if (!sortName) {
    return mbName;
  }

  // Check if the name is ASCII (latin characters only)
  // eslint-disable-next-line no-control-regex
  const isAscii = /^[\x00-\x7F]*$/.test(mbName);

  if (!isAscii) {
    return `${mbName} (${sortName})`;
  }

  return mbName;
}

export function ArtistDetails({ artistURI }: ArtistDetailsProps) {
  const { data: artists } = useArtists({ artists: [artistURI] });
  const artist = artists?.[artistURI];

  const { data: artistAlbums } = useAlbums({
    artists: artist ? [artist.artist_uri] : ["NO-ARTIST"],
  });

  const { data: artistCredits } = useArtistCredits(artistURI);

  if (!artist) return null;

  return (
    <>
      <h2>{artist.artist_name}</h2>
      <div className={styles.artistImageContainer}>
        <img src={artist.artist_image_url} className={styles.artistImage} />
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

      {artistCredits?.aliases && artistCredits.aliases.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3>Also Known As</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {artistCredits.aliases.map((alias) => {
              const displayName =
                alias.artist_name ||
                formatMBArtistName(
                  alias.artist_mb_name,
                  alias.artist_sort_name
                );
              return <Pill>{displayName}</Pill>;
            })}
          </div>
        </div>
      )}

      {artistCredits?.members && artistCredits.members.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3>Members</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {artistCredits.members.map((member) =>
              member.artist_uri ? (
                <ArtistPill
                  key={member.artist_uri}
                  artist={{
                    artist_uri: member.artist_uri,
                    artist_name:
                      member.artist_name ??
                      formatMBArtistName(
                        member.artist_mb_name!,
                        member.artist_sort_name
                      ),
                    artist_image_url: member.artist_image_url || "",
                    artist_followers: 0,
                    artist_liked_track_count: 0,
                    artist_popularity: 0,
                    artist_track_count: 0,
                    artist_stream_count: 0,
                  }}
                />
              ) : (
                <Pill>
                  {formatMBArtistName(
                    member.artist_mb_name!,
                    member.artist_sort_name
                  )}
                </Pill>
              )
            )}
          </div>
        </div>
      )}

      {artistCredits?.groups && artistCredits.groups.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3>Member Of</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {artistCredits.groups.map((group) => {
              const displayName =
                group.artist_name ||
                formatMBArtistName(
                  group.artist_mb_name,
                  group.artist_sort_name
                );
              return group.artist_uri ? (
                <RelatedArtistPill
                  key={group.artist_mbid}
                  artistUri={group.artist_uri}
                  artistName={displayName}
                  artistImageUrl={group.artist_image_url}
                />
              ) : (
                <span
                  key={group.artist_mbid}
                  style={{
                    padding: "4px 8px",
                    backgroundColor: "#f0f0f0",
                    borderRadius: 4,
                  }}
                >
                  {displayName}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {artistCredits?.subgroups && artistCredits.subgroups.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3>Subgroups</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {artistCredits.subgroups.map((subgroup) => {
              const displayName =
                subgroup.artist_name ||
                formatMBArtistName(
                  subgroup.artist_mb_name,
                  subgroup.artist_sort_name
                );
              return subgroup.artist_uri ? (
                <RelatedArtistPill
                  key={subgroup.artist_mbid}
                  artistUri={subgroup.artist_uri}
                  artistName={displayName}
                  artistImageUrl={subgroup.artist_image_url}
                />
              ) : (
                <span
                  key={subgroup.artist_mbid}
                  style={{
                    padding: "4px 8px",
                    backgroundColor: "#f0f0f0",
                    borderRadius: 4,
                  }}
                >
                  {displayName}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {artistCredits?.credits && artistCredits.credits.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3>Songwriting & Production Credits</h3>
          <div style={{ maxHeight: 400, overflowY: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #ddd" }}>
                  <th style={{ textAlign: "left", padding: 8 }}>Track</th>
                  <th style={{ textAlign: "left", padding: 8 }}>Credit Type</th>
                  <th style={{ textAlign: "left", padding: 8 }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {artistCredits.credits.map((credit, idx) => (
                  <tr
                    key={`${credit.recording_mbid}-${idx}`}
                    style={{ borderBottom: "1px solid #eee" }}
                  >
                    <td style={{ padding: 8 }}>
                      {credit.track_name || credit.recording_title}
                    </td>
                    <td style={{ padding: 8 }}>{credit.credit_type}</td>
                    <td style={{ padding: 8 }}>
                      {credit.credit_details || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <ArtistsStreamingHistoryStack onlyArtist={artistURI} />
      <ArtistStreamsLineChart height={300} onlyArtist={artistURI} />
    </>
  );
}

function RelatedArtistPill({
  artistUri,
  artistName,
  artistImageUrl,
}: {
  artistUri: string;
  artistName: string;
  artistImageUrl: string | null | undefined;
}) {
  const setFilters = useSetFilters();

  const onClick = () => {
    setFilters({ artists: [artistUri] });
  };

  return (
    <PillWithAvatar imageHref={artistImageUrl || ""} onClick={onClick}>
      {artistName}
    </PillWithAvatar>
  );
}
