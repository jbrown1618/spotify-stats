import "./global.css";

import { Anchor, Container, useMantineTheme } from "@mantine/core";

import { AlbumDetails } from "./details/AlbumDetails";
import { ArtistDetails } from "./details/ArtistDetails";
import { PlaylistDetails } from "./details/PlaylistDetails";
import { ProducerDetails } from "./details/ProducerDetails";
import { TrackDetails } from "./details/TrackDetails";
import { WrappedDetails } from "./details/WrappedDetails";
import { Filters } from "./Filters";
import { AlbumsSection } from "./sections/AlbumsSection";
import { ArtistsSection } from "./sections/ArtistsSection";
import { GenresSection } from "./sections/GenresSection";
import { LabelsSection } from "./sections/LabelsSection";
import { PlaylistsSection } from "./sections/PlaylistsSection";
import { ProducersSection } from "./sections/ProducersSection";
import { ReleaseYearsSection } from "./sections/ReleaseYearsSection";
import { TracksSection } from "./sections/TracksSection";
import { useFilters } from "./useFilters";

export function App() {
  const filters = useFilters();

  return (
    <>
      <HeaderBackground />
      <Container size="lg">
        <AppHeader />

        {filters.wrapped && <WrappedDetails />}
        {filters.tracks?.length === 1 && (
          <TrackDetails trackURI={filters.tracks[0]} />
        )}
        {filters.artists?.length === 1 && (
          <ArtistDetails artistURI={filters.artists[0]} />
        )}
        {filters.albums?.length === 1 && (
          <AlbumDetails albumURI={filters.albums[0]} />
        )}
        {filters.playlists?.length === 1 && (
          <PlaylistDetails playlistURI={filters.playlists[0]} />
        )}
        {filters.producers?.length === 1 && (
          <ProducerDetails mbid={filters.producers[0]} />
        )}

        {filters.labels?.length === 1 && <h2>{filters.labels[0]}</h2>}
        {filters.genres?.length === 1 && <h2>{filters.genres[0]}</h2>}
        {filters.years?.length === 1 && (
          <h2>Tracks released in {filters.years[0]}</h2>
        )}

        <div>
          <TracksSection />
          <ArtistsSection />
          <AlbumsSection />
          <PlaylistsSection />
          <LabelsSection />
          <GenresSection />
          <ProducersSection />
          <ReleaseYearsSection />
        </div>

        <AppFooter />
      </Container>
    </>
  );
}

function AppHeader() {
  return (
    <nav
      style={{
        display: "flex",
        justifyContent: "space-between",
      }}
    >
      <h1 style={{ margin: 0, whiteSpace: "nowrap" }}>Spotify Stats</h1>
      <Filters />
    </nav>
  );
}

function HeaderBackground() {
  const t = useMantineTheme();
  return (
    <div
      style={{
        width: "100%",
        height: 40,
        backgroundColor: t.colors.green[9],
        position: "absolute",
        zIndex: -1,
      }}
    />
  );
}

function AppFooter() {
  return (
    <footer style={{ padding: 16, textAlign: "center" }}>
      <Anchor
        href="https://www.github.com/jbrown1618/spotify-stats"
        target="_blank"
        underline="hover"
      >
        jbrown1618/spotify-stats
      </Anchor>
    </footer>
  );
}
