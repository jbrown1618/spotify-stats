import "./global.css";

import { Container } from "@mantine/core";

import { Backdrop } from "./Backdrop";
import { TextSkeleton } from "./design/TextSkeleton";
import { AlbumDetails } from "./details/AlbumDetails";
import { ArtistDetails } from "./details/ArtistDetails";
import { PlaylistDetails } from "./details/PlaylistDetails";
import { ProducerDetails } from "./details/ProducerDetails";
import { TrackDetails } from "./details/TrackDetails";
import { Header } from "./Header";
import { AlbumsSection } from "./sections/AlbumsSection";
import { ArtistsSection } from "./sections/ArtistsSection";
import { GenresSection } from "./sections/GenresSection";
import { InsightsSection } from "./sections/InsightsSection";
import { LabelsSection } from "./sections/LabelsSection";
import { PlaylistsSection } from "./sections/PlaylistsSection";
import { ProducersSection } from "./sections/ProducersSection";
import { RecommendationsSection } from "./sections/RecommendationsSection";
import { ReleaseYearsSection } from "./sections/ReleaseYearsSection";
import { TracksSection } from "./sections/TracksSection";
import { SectionTabs, useSectionDefs } from "./SectionTabs";
import { SpotifyAuthBanner } from "./SpotifyAuthBanner";
import {
  useAlbums,
  useArtists,
  usePlaylists,
  useProducers,
  useTracks,
} from "./useApi";
import { useFilters } from "./useFilters";
import { namedWrappedOptions } from "./utils";

function DetailsContent() {
  const filters = useFilters();
  return (
    <>
      {filters.tracks && <TrackDetails trackURI={filters.tracks} />}
      {filters.artists && <ArtistDetails artistURI={filters.artists} />}
      {filters.producers && <ProducerDetails mbid={filters.producers} />}
    </>
  );
}

function TracksOverviewContent() {
  const filters = useFilters();

  if (!filters.albums && !filters.playlists) {
    return null;
  }

  return (
    <>
      {filters.albums && <AlbumDetails albumURI={filters.albums} />}
      {filters.playlists && <PlaylistDetails playlistURI={filters.playlists} />}
    </>
  );
}

function DetailsTitle() {
  const filters = useFilters();

  const { items: tracks } = useTracks(
    filters.tracks ? { filters: { tracks: filters.tracks } } : undefined
  );
  const { items: artists } = useArtists(
    filters.artists ? { filters: { artists: filters.artists } } : undefined
  );
  const { items: albums } = useAlbums(
    filters.albums ? { filters: { albums: filters.albums } } : undefined
  );
  const { items: playlists } = usePlaylists(
    filters.playlists ? { filters: { playlists: filters.playlists } } : undefined
  );
  const { items: producers } = useProducers(
    filters.producers ? { filters: { producers: filters.producers } } : undefined
  );

  const trackName = filters.tracks ? tracks?.[0]?.track_name : null;
  const artistName = filters.artists
    ? artists?.find((a) => a.artist_uri === filters.artists)?.artist_name
    : null;
  const albumName = filters.albums
    ? albums?.find((a) => a.album_uri === filters.albums)?.album_name
    : null;
  const playlistName = filters.playlists
    ? playlists?.find((p) => p.playlist_uri === filters.playlists)?.playlist_name
    : null;
  const producerName = filters.producers
    ? producers?.find((p) => p.producer_mbid === filters.producers)?.producer_name
    : null;
  const wrappedLabel = filters.wrapped
    ? namedWrappedOptions().find((o) => o.value === filters.wrapped)?.label ??
      filters.wrapped
    : null;

  const title =
    wrappedLabel ? `Wrapped: ${wrappedLabel}` :
    trackName ?? artistName ?? albumName ?? playlistName ?? producerName ??
    filters.labels ??
    filters.genres ??
    (filters.years !== undefined && filters.years !== null
      ? `Tracks released in ${filters.years}`
      : null);

  const hasDetailFilter = !!(
    filters.wrapped ||
    filters.tracks ||
    filters.artists ||
    filters.albums ||
    filters.playlists ||
    filters.producers ||
    filters.labels ||
    filters.genres ||
    filters.years !== undefined && filters.years !== null
  );

  if (!hasDetailFilter) return null;
  if (!title) return <TextSkeleton style="h2" />;
  return <h2>{title}</h2>;
}

export function App() {
  const sections = useSectionDefs({
    details: <DetailsContent />,
    insights: <InsightsSection />,
    tracks: <TracksSection overview={<TracksOverviewContent />} />,
    artists: <ArtistsSection />,
    albums: <AlbumsSection />,
    playlists: <PlaylistsSection />,
    labels: <LabelsSection />,
    genres: <GenresSection />,
    producers: <ProducersSection />,
    years: <ReleaseYearsSection />,
    recommendations: <RecommendationsSection />,
  });

  return (
    <>
      <Backdrop />
      <Container size="lg">
        <Header />
        <SpotifyAuthBanner />
        <DetailsTitle />
        <SectionTabs sections={sections} />
      </Container>
    </>
  );
}
