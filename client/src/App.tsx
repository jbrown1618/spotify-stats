import "./global.css";

import { Anchor, Container, useMantineTheme } from "@mantine/core";

import { AlbumDetails } from "./details/AlbumDetails";
import { ArtistDetails } from "./details/ArtistDetails";
import { Filters } from "./Filters";
import { AlbumsSection } from "./sections/AlbumsSection";
import { ArtistsSection } from "./sections/ArtistsSection";
import { GenresSection } from "./sections/GenresSection";
import { LabelsSection } from "./sections/LabelsSection";
import { PlaylistsSection } from "./sections/PlaylistsSection";
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

        {filters.artists?.length === 1 && (
          <ArtistDetails artistURI={filters.artists[0]} />
        )}

        {filters.albums?.length === 1 && (
          <AlbumDetails albumURI={filters.albums[0]} />
        )}

        <div>
          <TracksSection />
          <ArtistsSection />
          <AlbumsSection />
          <PlaylistsSection />
          <LabelsSection />
          <GenresSection />
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
