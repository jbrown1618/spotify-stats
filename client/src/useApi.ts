import { useQuery } from "@tanstack/react-query";

import {
  ActiveFilters,
  AlbumRank,
  ArtistRank,
  FilterOptions,
  getAlbums,
  getAlbumsStreamingHistory,
  getAlbumsStreamsByMonth,
  getArtists,
  getArtistsStreamingHistory,
  getArtistsStreamsByMonth,
  getFilterOptions,
  getGenres,
  getLabels,
  getPlaylists,
  getProducers,
  getReleaseYears,
  getTrack,
  getTracksStreamingHistory,
  getTracksStreamsByMonth,
  searchTracks,
  toFiltersQuery,
  Track,
  TrackDetails,
  TrackRank,
} from "./api";
import {
  mostStreamedAlbums,
  mostStreamedArtists,
  mostStreamedTracks,
} from "./sorting";
import { useFilters } from "./useFilters";
import { countUniqueAsOfDates, countUniqueMonths } from "./utils";

const defaultQueryOptions = {
  staleTime: 1000 * 60 * 60,
  gcTime: 1000 * 60 * 60,
};

export function useFilterOptions() {
  return useQuery<FilterOptions>({
    ...defaultQueryOptions,
    queryKey: ["filter-options"],
    queryFn: async () => getFilterOptions(),
  });
}

export function useTracks(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const query = toFiltersQuery(filters ?? globalFilters);
  return useQuery<Record<string, Track>>({
    ...defaultQueryOptions,
    queryKey: ["tracks", query],
    queryFn: async () => searchTracks(filters ?? globalFilters),
  });
}

export function useTrack(uri: string) {
  const { wrapped } = useFilters();
  return useQuery<TrackDetails>({
    ...defaultQueryOptions,
    queryKey: ["track", uri, wrapped],
    queryFn: async () => getTrack(uri, wrapped),
  });
}

export function usePlaylists(filters?: ActiveFilters) {
  return useTracksDependentQuery("playlists", getPlaylists, {}, filters);
}

export function useArtists(filters?: ActiveFilters) {
  return useTracksDependentQuery("artists", getArtists, {}, filters);
}

export function useAlbums(filters?: ActiveFilters) {
  return useTracksDependentQuery("albums", getAlbums, {}, filters);
}

export function useLabels(filters?: ActiveFilters) {
  return useTracksDependentQuery("labels", getLabels, [], filters);
}

export function useGenres(filters?: ActiveFilters) {
  return useTracksDependentQuery("genres", getGenres, [], filters);
}

export function useReleaseYears(filters?: ActiveFilters) {
  return useTracksDependentQuery("release-years", getReleaseYears, [], filters);
}

export function useProducers(filters?: ActiveFilters) {
  return useTracksDependentQuery("producers", getProducers, {}, filters);
}

export function useTracksStreamingHistory() {
  const filters = useFilters();
  const { data: tracks } = useTracks();

  const topTenUris = Object.values(tracks ?? {})
    .sort(mostStreamedTracks)
    .slice(0, 10)
    .map((t) => t.track_uri);

  const tracksFilter = { tracks: topTenUris, wrapped: filters.wrapped };
  const query = toFiltersQuery(tracksFilter);
  const result = useQuery<TrackRank[]>({
    ...defaultQueryOptions,
    queryKey: ["tracks-streaming-history", query],
    enabled: !!tracks,
    queryFn: async () => getTracksStreamingHistory(tracksFilter),
  });

  const shouldRender = !result.data || countUniqueAsOfDates(result.data) > 4;

  return { ...result, shouldRender };
}

export function useArtistsStreamingHistory() {
  const filters = useFilters();
  const { data: artists } = useArtists();

  const topTenUris = Object.values(artists ?? {})
    .sort(mostStreamedArtists)
    .slice(0, 10)
    .map((t) => t.artist_uri);

  const artistsFilter = { artists: topTenUris, wrapped: filters.wrapped };
  const query = toFiltersQuery(artistsFilter);
  const result = useQuery<ArtistRank[]>({
    ...defaultQueryOptions,
    queryKey: ["artists-streaming-history", query],
    enabled: !!artists,
    queryFn: async () => getArtistsStreamingHistory(artistsFilter),
  });

  const shouldRender = !result.data || countUniqueAsOfDates(result.data) > 4;

  return { ...result, shouldRender };
}

export function useAlbumsStreamingHistory() {
  const filters = useFilters();
  const { data: albums } = useAlbums();

  const topTenUris = Object.values(albums ?? {})
    .sort(mostStreamedAlbums)
    .slice(0, 10)
    .map((t) => t.album_uri);

  const albumsFilter = { albums: topTenUris, wrapped: filters.wrapped };
  const query = toFiltersQuery(albumsFilter);
  const result = useQuery<AlbumRank[]>({
    ...defaultQueryOptions,
    queryKey: ["albums-streaming-history", query],
    enabled: !!albums,
    queryFn: async () => getAlbumsStreamingHistory(albumsFilter),
  });

  const shouldRender = !result.data || countUniqueAsOfDates(result.data) > 4;

  return { ...result, shouldRender };
}

export function useTracksStreamsByMonth() {
  function getTopFiveTracksStreamsByMonth(
    filters: ActiveFilters,
    tracks: Record<string, Track>
  ) {
    const topFiveUris = Object.values(tracks ?? {})
      .sort(mostStreamedTracks)
      .slice(0, 5)
      .map((t) => t.track_uri);
    return getTracksStreamsByMonth({ ...filters, tracks: topFiveUris });
  }

  const result = useTracksDependentQuery(
    "tracks-streaming-history",
    getTopFiveTracksStreamsByMonth,
    {}
  );

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

export function useArtistsStreamsByMonth() {
  const filters = useFilters();
  const { data: artists } = useArtists();

  const topFiveUris = Object.values(artists ?? {})
    .sort(mostStreamedArtists)
    .slice(0, 5)
    .map((t) => t.artist_uri);

  const artistsFilter = { artists: topFiveUris, wrapped: filters.wrapped };
  const query = toFiltersQuery(artistsFilter);
  const result = useQuery<
    Record<string, Record<number, Record<number, number>>>
  >({
    ...defaultQueryOptions,
    queryKey: ["artists-streams-by-month", query],
    enabled: !!artists,
    queryFn: async () => getArtistsStreamsByMonth(artistsFilter),
  });

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

export function useAlbumsStreamsByMonth() {
  const filters = useFilters();
  const { data: albums } = useAlbums();

  const topFiveUris = Object.values(albums ?? {})
    .sort(mostStreamedAlbums)
    .slice(0, 5)
    .map((t) => t.album_uri);

  const albumsFilter = { albums: topFiveUris, wrapped: filters.wrapped };
  const query = toFiltersQuery(albumsFilter);
  const result = useQuery<
    Record<string, Record<number, Record<number, number>>>
  >({
    ...defaultQueryOptions,
    queryKey: ["albums-streams-by-month", query],
    enabled: !!albums,
    queryFn: async () => getAlbumsStreamsByMonth(albumsFilter),
  });

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

function useTracksDependentQuery<T>(
  key: string,
  getValue: (
    filters: ActiveFilters,
    tracks: Record<string, Track>
  ) => Promise<T>,
  defaultValue: T,
  filters?: ActiveFilters
) {
  const globalFilters = useFilters();
  filters ??= globalFilters;
  const query =
    toFiltersQuery({ wrapped: filters.wrapped, ...filters }) ||
    DEFAULT_QUERY_KEY;

  const { data: tracks } = useTracks(filters);
  const tracksFilter = {
    tracks: tracks ? Object.keys(tracks) : [],
    wrapped: filters.wrapped,
  };

  const result = useQuery<T>({
    ...defaultQueryOptions,
    enabled: !!tracks,
    queryKey: [key, query],
    queryFn: async () =>
      tracksFilter.tracks.length === 0
        ? defaultValue
        : getValue(tracksFilter, tracks!),
  });

  return { ...result, tracks };
}

// If a piece of a query key is an empty string, the request will not fire
const DEFAULT_QUERY_KEY = "DEFAULT";
