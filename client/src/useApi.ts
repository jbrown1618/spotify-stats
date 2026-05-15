import { useInfiniteQuery, useQuery } from "@tanstack/react-query";

import {
  ActiveFilters,
  Album,
  AlbumRank,
  Artist,
  ArtistCreditsData,
  ArtistRank,
  Credit,
  FilterOptions,
  Genre,
  Label,
  PaginatedResponse,
  Playlist,
  Producer,
  getAlbums,
  getAlbumsStreamingHistory,
  getAlbumsStreamsByMonth,
  getArtistCredits,
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
  ReleaseYear,
  searchTracks,
  StreamsByMonth,
  toFiltersQuery,
  Track,
  TrackDetails,
  TrackRank,
} from "./api";
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
  return useQuery<PaginatedResponse<Track>>({
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
    select: (data) => data.total,
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
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery<PaginatedResponse<Playlist>>({
    ...defaultQueryOptions,
    queryKey: ["playlists", query],
    queryFn: async () => getPlaylists(activeFilters),
  });
}

export function useArtists(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery<PaginatedResponse<Artist>>({
    ...defaultQueryOptions,
    queryKey: ["artists", query],
    queryFn: async () => getArtists(activeFilters),
  });
}

export function useArtistCredits(artistUri: string) {
  return useQuery<ArtistCreditsData>({
    ...defaultQueryOptions,
    queryKey: ["artist-credits", artistUri],
    queryFn: async () => getArtistCredits(artistUri),
  });
}

export function useAlbums(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery<PaginatedResponse<Album>>({
    ...defaultQueryOptions,
    queryKey: ["albums", query],
    queryFn: async () => getAlbums(activeFilters),
  });
}

export function useLabels(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery<PaginatedResponse<Label>>({
    ...defaultQueryOptions,
    queryKey: ["labels", query],
    queryFn: async () => getLabels(activeFilters),
  });
}

export function useGenres(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery<PaginatedResponse<Genre>>({
    ...defaultQueryOptions,
    queryKey: ["genres", query],
    queryFn: async () => getGenres(activeFilters),
  });
}

export function useReleaseYears(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery<PaginatedResponse<ReleaseYear>>({
    ...defaultQueryOptions,
    queryKey: ["release-years", query],
    queryFn: async () => getReleaseYears(activeFilters),
  });
}

export function useProducers(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery<PaginatedResponse<Producer>>({
    ...defaultQueryOptions,
    queryKey: ["producers", query],
    queryFn: async () => getProducers(activeFilters),
  });
}

export function useTracksStreamingHistory() {
  const filters = useFilters();
  const query = toFiltersQuery(filters) || DEFAULT_QUERY_KEY;
  const result = useQuery<TrackRank[]>({
    ...defaultQueryOptions,
    queryKey: ["tracks-streaming-history", query],
    queryFn: async () => getTracksStreamingHistory({ ...filters, n: 10 }),
  });

  const shouldRender = !result.data || countUniqueAsOfDates(result.data) > 4;

  return { ...result, shouldRender };
}

export function useArtistsStreamingHistory() {
  const filters = useFilters();
  const query = toFiltersQuery(filters) || DEFAULT_QUERY_KEY;
  const result = useQuery<ArtistRank[]>({
    ...defaultQueryOptions,
    queryKey: ["artists-streaming-history", query],
    queryFn: async () => getArtistsStreamingHistory({ ...filters, n: 10 }),
  });

  const shouldRender = !result.data || countUniqueAsOfDates(result.data) > 4;

  return { ...result, shouldRender };
}

export function useAlbumsStreamingHistory() {
  const filters = useFilters();
  const query = toFiltersQuery(filters) || DEFAULT_QUERY_KEY;
  const result = useQuery<AlbumRank[]>({
    ...defaultQueryOptions,
    queryKey: ["albums-streaming-history", query],
    queryFn: async () => getAlbumsStreamingHistory({ ...filters, n: 10 }),
  });

  const shouldRender = !result.data || countUniqueAsOfDates(result.data) > 4;

  return { ...result, shouldRender };
}

export function useTracksStreamsByMonth(n: number = 5) {
  const filters = useFilters();
  const query = toFiltersQuery(filters) || DEFAULT_QUERY_KEY;
  const result = useQuery<StreamsByMonth>({
    ...defaultQueryOptions,
    queryKey: ["tracks-streams-by-month", query, n],
    queryFn: async () => getTracksStreamsByMonth({ ...filters, n }),
  });

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

export function useArtistsStreamsByMonth(n: number = 5) {
  const filters = useFilters();
  const query = toFiltersQuery(filters) || DEFAULT_QUERY_KEY;
  const result = useQuery<StreamsByMonth>({
    ...defaultQueryOptions,
    queryKey: ["artists-streams-by-month", query, n],
    queryFn: async () => getArtistsStreamsByMonth({ ...filters, n }),
  });

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

export function useAlbumsStreamsByMonth(n: number = 5) {
  const filters = useFilters();
  const query = toFiltersQuery(filters) || DEFAULT_QUERY_KEY;
  const result = useQuery<StreamsByMonth>({
    ...defaultQueryOptions,
    queryKey: ["albums-streams-by-month", query, n],
    queryFn: async () => getAlbumsStreamsByMonth({ ...filters, n }),
  });

  const shouldRender = !result.data || countUniqueMonths(result.data) > 3;

  return { ...result, shouldRender };
}

export function useRecommendations() {
  const filters = useFilters();
  const query = toFiltersQuery(filters) || DEFAULT_QUERY_KEY;
  return useQuery<Recommendations>({
    ...defaultQueryOptions,
    queryKey: ["recommendations", query],
    queryFn: async () => getRecommendations(filters),
  });
}

const PAGE_SIZE = 24;

function usePaginatedQuery<T>(
  key: string,
  sort: string,
  fetcher: (
    filters: ActiveFilters & { limit: number; offset: number; sort: string }
  ) => Promise<PaginatedResponse<T>>,
  filters?: ActiveFilters
) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;

  return useInfiniteQuery<PaginatedResponse<T>>({
    ...defaultQueryOptions,
    queryKey: [key, query, sort],
    queryFn: async ({ pageParam = 0 }) =>
      fetcher({ ...activeFilters, limit: PAGE_SIZE, offset: pageParam, sort }),
    initialPageParam: 0,
    getNextPageParam: (_lastPage, allPages) => {
      const total = allPages[0]?.total ?? 0;
      const loaded = allPages.reduce((n, p) => n + p.items.length, 0);
      return loaded < total ? loaded : undefined;
    },
  });
}

export function usePaginatedTracks(sort: string) {
  return usePaginatedQuery("tracks-paginated", sort, searchTracks);
}

export function usePaginatedArtists(sort: string) {
  return usePaginatedQuery("artists-paginated", sort, getArtists);
}

export function usePaginatedAlbums(sort: string) {
  return usePaginatedQuery("albums-paginated", sort, getAlbums);
}

export function usePaginatedPlaylists() {
  return usePaginatedQuery(
    "playlists-paginated",
    "Most liked tracks",
    getPlaylists
  );
}

export function usePaginatedLabels() {
  return usePaginatedQuery(
    "labels-paginated",
    "Most liked tracks",
    getLabels
  );
}

export function usePaginatedGenres() {
  return usePaginatedQuery(
    "genres-paginated",
    "Most liked tracks",
    getGenres
  );
}

export function usePaginatedReleaseYears() {
  return usePaginatedQuery(
    "release-years-paginated",
    "Most liked tracks",
    getReleaseYears
  );
}

export function usePaginatedProducers() {
  return usePaginatedQuery(
    "producers-paginated",
    "Most tracks",
    getProducers
  );
}

// If a piece of a query key is an empty string, the request will not fire
const DEFAULT_QUERY_KEY = "DEFAULT";
