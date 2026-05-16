import { ActiveFilters } from "../api";
import { ArtistPill } from "../list-items/ArtistPill";
import { mostStreamedArtists } from "../sorting";
import { useArtists } from "../useApi";
import styles from "./ArtistPills.module.css";
import { PillSkeleton } from "./PillDesign";

export function ArtistPills({ filters }: { filters: ActiveFilters }) {
  const { items: artists } = useArtists({ filters });
  if (!artists) {
    return <PillSkeleton />;
  }

  return (
    <div className={styles.artistPills}>
      {artists
        .sort(mostStreamedArtists)
        .map((artist) => (
          <ArtistPill key={artist.artist_uri} artist={artist} />
        ))}
    </div>
  );
}
