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
import { LabelsSection } from "./sections/LabelsSection";
import { PlaylistsSection } from "./sections/PlaylistsSection";
import { ProducersSection } from "./sections/ProducersSection";
import { RecommendationsSection } from "./sections/RecommendationsSection";
import { ReleaseYearsSection } from "./sections/ReleaseYearsSection";
import { TracksSection } from "./sections/TracksSection";
import { SectionTabs, useSectionDefs } from "./SectionTabs";
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
      {filters.tracks?.length === 1 && (
        <TrackDetails trackURI={filters.tracks[0]} />
      )}
      {filters.artists?.length === 1 && (
        <ArtistDetails artistURI={filters.artists[0]} />
      )}
      {filters.producers?.length === 1 && (
        <ProducerDetails mbid={filters.producers[0]} />
      )}
    </>
  );
}

function TracksOverviewContent() {
  const filters = useFilters();

  if (filters.albums?.length !== 1 && filters.playlists?.length !== 1) {
    return null;
  }

  return (
    <>
      {filters.albums?.length === 1 && (
        <AlbumDetails albumURI={filters.albums[0]} />
      )}
      {filters.playlists?.length === 1 && (
        <PlaylistDetails playlistURI={filters.playlists[0]} />
      )}
    </>
  );
}

function DetailsTitle() {
  const filters = useFilters();

  const { items: tracks } = useTracks(
    filters.tracks?.length === 1
      ? { filters: { tracks: filters.tracks } }
      : undefined
  );
  const { items: artists } = useArtists(
    filters.artists?.length === 1
      ? { filters: { artists: filters.artists } }
      : undefined
  );
  const { items: albums } = useAlbums(
    filters.albums?.length === 1
      ? { filters: { albums: filters.albums } }
      : undefined
  );
  const { items: playlists } = usePlaylists(
    filters.playlists?.length === 1
      ? { filters: { playlists: filters.playlists } }
      : undefined
  );
  const { items: producers } = useProducers(
    filters.producers?.length === 1
      ? { filters: { producers: filters.producers } }
      : undefined
  );

  const trackName = filters.tracks?.length === 1 ? tracks?.[0]?.track_name : null;
  const artistName = filters.artists?.length === 1
    ? artists?.find((a) => a.artist_uri === filters.artists?.[0])?.artist_name
    : null;
  const albumName = filters.albums?.length === 1
    ? albums?.find((a) => a.album_uri === filters.albums?.[0])?.album_name
    : null;
  const playlistName = filters.playlists?.length === 1
    ? playlists?.find((p) => p.playlist_uri === filters.playlists?.[0])?.playlist_name
    : null;
  const producerName = filters.producers?.length === 1
    ? producers?.find((p) => p.producer_mbid === filters.producers?.[0])?.producer_name
    : null;
  const wrappedLabel = filters.wrapped
    ? namedWrappedOptions().find((o) => o.value === filters.wrapped)?.label ??
      filters.wrapped
    : null;

  const title =
    wrappedLabel ? `Wrapped: ${wrappedLabel}` :
    trackName ?? artistName ?? albumName ?? playlistName ?? producerName ??
    (filters.labels?.length === 1 ? filters.labels[0] : null) ??
    (filters.genres?.length === 1 ? filters.genres[0] : null) ??
    (filters.years?.length === 1 ? `Tracks released in ${filters.years[0]}` : null);

  const hasDetailFilter = !!(
    filters.wrapped ||
    filters.tracks?.length === 1 ||
    filters.artists?.length === 1 ||
    filters.albums?.length === 1 ||
    filters.playlists?.length === 1 ||
    filters.producers?.length === 1 ||
    filters.labels?.length === 1 ||
    filters.genres?.length === 1 ||
    filters.years?.length === 1
  );

  if (!hasDetailFilter) return null;
  if (!title) return <TextSkeleton style="h2" />;
  return <h2>{title}</h2>;
}

export function App() {
  const sections = useSectionDefs({
    details: <DetailsContent />,
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
        <DetailsTitle />
        <SectionTabs sections={sections} />
      </Container>
    </>
  );
}
