import { useInfiniteQuery, useQuery } from "@tanstack/react-query";

import {
  ActiveFilters,
  AlbumRank,
  ArtistCreditsData,
  ArtistRank,
  Credit,
  FilterOptions,
  PaginatedResponse,
  PaginationParams,
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
  searchTracks,
  StreamsByMonth,
  toFiltersQuery,
  TrackDetails,
  TrackRank,
} from "./api";
import { useFilters } from "./useFilters";
import { countUniqueAsOfDates, countUniqueMonths } from "./utils";

// If a piece of a query key is an empty string, the request will not fire
const DEFAULT_QUERY_KEY = "DEFAULT";

export const PAGE_SIZE = 24;

const defaultQueryOptions = {
  staleTime: 1000 * 60 * 60,
  gcTime: 1000 * 60 * 60,
};

// --- Generic entity hook (always useInfiniteQuery) ---

export interface EntityQueryOptions {
  sort?: string;
  limit?: number;
  filters?: ActiveFilters;
}

function useEntityQuery<T>(
  key: string,
  fetcher: (params: ActiveFilters & Partial<PaginationParams>) => Promise<PaginatedResponse<T>>,
  opts?: EntityQueryOptions,
) {
  const globalFilters = useFilters();
  const filters = opts?.filters ?? globalFilters;
  const query = toFiltersQuery(filters) || DEFAULT_QUERY_KEY;
  const { sort, limit } = opts ?? {};

  const result = useInfiniteQuery<PaginatedResponse<T>>({
    ...defaultQueryOptions,
    queryKey: [key, query, sort ?? "default", limit ?? "all"],
    queryFn: async ({ pageParam = 0 }) =>
      fetcher({
        ...filters,
        ...(sort ? { sort } : {}),
        ...(limit ? { limit, offset: pageParam as number } : {}),
      }),
    initialPageParam: 0,
    getNextPageParam: (_lastPage, allPages) => {
      if (!limit) return undefined;
      const total = allPages[0]?.total ?? 0;
      const loaded = allPages.reduce((n, p) => n + p.items.length, 0);
      return loaded < total ? loaded : undefined;
    },
  });

  return {
    ...result,
    items: result.data?.pages.flatMap((p) => p.items),
    total: result.data?.pages[0]?.total ?? 0,
  };
}

// --- Entity hooks ---

export const useTracks = (opts?: EntityQueryOptions) =>
  useEntityQuery("tracks", searchTracks, opts);

export const useArtists = (opts?: EntityQueryOptions) =>
  useEntityQuery("artists", getArtists, opts);

export const useAlbums = (opts?: EntityQueryOptions) =>
  useEntityQuery("albums", getAlbums, opts);

export const usePlaylists = (opts?: EntityQueryOptions) =>
  useEntityQuery("playlists", getPlaylists, opts);

export const useLabels = (opts?: EntityQueryOptions) =>
  useEntityQuery("labels", getLabels, opts);

export const useGenres = (opts?: EntityQueryOptions) =>
  useEntityQuery("genres", getGenres, opts);

export const useReleaseYears = (opts?: EntityQueryOptions) =>
  useEntityQuery("release-years", getReleaseYears, opts);

export const useProducers = (opts?: EntityQueryOptions) =>
  useEntityQuery("producers", getProducers, opts);

// --- Tracks count ---

export function useTracksCount(filters?: ActiveFilters) {
  const globalFilters = useFilters();
  const activeFilters = filters ?? globalFilters;
  const query = toFiltersQuery(activeFilters) || DEFAULT_QUERY_KEY;
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["tracks-count", query],
    queryFn: async () => searchTracks(activeFilters),
    select: (data) => data.total,
  });
}

// --- Specialized hooks ---

export function useFilterOptions() {
  return useQuery<FilterOptions>({
    ...defaultQueryOptions,
    queryKey: ["filter-options"],
    queryFn: async () => getFilterOptions(),
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

export function useArtistCredits(artistUri: string) {
  return useQuery<ArtistCreditsData>({
    ...defaultQueryOptions,
    queryKey: ["artist-credits", artistUri],
    queryFn: async () => getArtistCredits(artistUri),
  });
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

// --- Streaming history hooks ---

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
