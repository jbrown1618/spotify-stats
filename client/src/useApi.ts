import { useQuery } from "@tanstack/react-query";

import {
  ActiveFilters,
  AlbumRank,
  ArtistRank,
  Credit,
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
  getRecommendations,
  getReleaseYears,
  getTrack,
  getTrackCredits,
  getTracksStreamingHistory,
  getTracksStreamsByMonth,
  Recommendations,
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
  const activeFilters = filters ?? globalFilters

  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery<Record<string, Track>>({
    ...defaultQueryOptions,
    queryKey: ["tracks", query],
    queryFn: async () => searchTracks(activeFilters),
  });
}

export function useTracksCount(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters

  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["tracks", query],
    queryFn: async () => searchTracks(activeFilters),
    select: (data) => Object.keys(data).length,
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

export function useTrackCredits(uri: string) {
  return useQuery<Credit[]>({
    ...defaultQueryOptions,
    queryKey: ["track-credits", uri],
    queryFn: async () => getTrackCredits(uri),
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

export function useTracksStreamsByMonth(n: number = 5) {
  function getTopNTracksStreamsByMonth(
    filters: ActiveFilters,
    tracks: Record<string, Track>
  ) {
    const topNUris = Object.values(tracks ?? {})
      .sort(mostStreamedTracks)
      .slice(0, n)
      .map((t) => t.track_uri);
    return getTracksStreamsByMonth({ ...filters, tracks: topNUris });
  }

  const result = useTracksDependentQuery(
    "tracks-streams-by-month-" + n,
    getTopNTracksStreamsByMonth,
    {}
  );

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

export function useArtistsStreamsByMonth(n: number = 5) {
  const filters = useFilters();
  const { data: artists } = useArtists();

  const topNUris = Object.values(artists ?? {})
    .sort(mostStreamedArtists)
    .slice(0, n)
    .map((t) => t.artist_uri);

  const artistsFilter = { artists: topNUris, wrapped: filters.wrapped };
  const query = toFiltersQuery(artistsFilter);
  const result = useQuery<
    Record<string, Record<number, Record<number, number>>>
  >({
    ...defaultQueryOptions,
    queryKey: ["artists-streams-by-month", query, n],
    enabled: !!artists,
    queryFn: async () => getArtistsStreamsByMonth(artistsFilter),
  });

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

export function useAlbumsStreamsByMonth(n: number = 5) {
  const filters = useFilters();
  const { data: albums } = useAlbums();

  const topNUris = Object.values(albums ?? {})
    .sort(mostStreamedAlbums)
    .slice(0, n)
    .map((t) => t.album_uri);

  const albumsFilter = { albums: topNUris, wrapped: filters.wrapped };
  const query = toFiltersQuery(albumsFilter);
  const result = useQuery<
    Record<string, Record<number, Record<number, number>>>
  >({
    ...defaultQueryOptions,
    queryKey: ["albums-streams-by-month", query, n],
    enabled: !!albums,
    queryFn: async () => getAlbumsStreamsByMonth(albumsFilter),
  });

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

export function useRecommendations() {
  const filters = useFilters();
  const query = toFiltersQuery({ wrapped: filters.wrapped, ...filters }) || DEFAULT_QUERY_KEY;

  const { data: tracks, isSuccess } = useTracks(filters);
  
  // When no filters are applied, don't pass track URIs to avoid performance issues
  // The server will handle unfiltered queries more efficiently without URIs
  const hasFilters = Object.keys(filters).length > 0;
  const tracksFilter = {
    tracks: hasFilters ? (tracks ? Object.keys(tracks) : []) : undefined,
    wrapped: filters.wrapped,
  };

  const result = useQuery<Recommendations>({
    ...defaultQueryOptions,
    enabled: isSuccess,
    queryKey: ["recommendations", query],
    queryFn: async () =>
      hasFilters && tracksFilter.tracks && tracksFilter.tracks.length === 0
        ? {}
        : getRecommendations(tracksFilter),
  });

  return { ...result, tracks };
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

  const { data: tracks, isSuccess } = useTracks(filters);
  const tracksFilter = {
    tracks: tracks ? Object.keys(tracks) : [],
    wrapped: filters.wrapped,
  };

  const result = useQuery<T>({
    ...defaultQueryOptions,
    enabled: isSuccess,
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
