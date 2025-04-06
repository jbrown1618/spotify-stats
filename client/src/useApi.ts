import { useQuery } from "@tanstack/react-query";

import {
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
  getReleaseYears,
  getSummary,
  getTrack,
  getTracksStreamingHistory,
  getTracksStreamsByMonth,
  searchTracks,
  toFiltersQuery,
} from "./api";
import { useFilters } from "./useFilters";

const defaultQueryOptions = {
  staleTime: 1000 * 60 * 60,
  gcTime: 1000 * 60 * 60,
};

export function useSummary() {
  const filters = useFilters();
  const query = toFiltersQuery(filters);
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["summary", query],
    queryFn: async () => getSummary(query),
  });
}

export function useFilterOptions() {
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["filter-options"],
    queryFn: async () => getFilterOptions(),
  });
}

export function useTracks() {
  const filters = useFilters();
  const query = toFiltersQuery(filters);
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["tracks", query],
    queryFn: async () => searchTracks(query),
  });
}

export function useTrack(uri: string) {
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["track", uri],
    queryFn: async () => getTrack(uri),
  });
}

export function usePlaylists() {
  const { data: tracks } = useTracks();
  const uris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: uris });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["playlists", query],
    queryFn: async () => getPlaylists(query),
  });
}

export function useArtists() {
  const { data: tracks } = useTracks();
  const uris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: uris });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["artists", query],
    queryFn: async () => getArtists(query),
  });
}

export function useAlbums() {
  const { data: tracks } = useTracks();
  const uris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: uris });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["albums", query],
    queryFn: async () => getAlbums(query),
  });
}

export function useLabels() {
  const { data: tracks } = useTracks();
  const uris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: uris });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["labels", query],
    queryFn: async () => getLabels(query),
  });
}

export function useGenres() {
  const { data: tracks } = useTracks();
  const uris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: uris });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["genres", query],
    queryFn: async () => getGenres(query),
  });
}

export function useReleaseYears() {
  const { data: tracks } = useTracks();
  const uris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: uris });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["release-years", query],
    queryFn: async () => getReleaseYears(query),
  });
}

export function useTracksStreamingHistory(trackUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({ tracks: trackUris, wrapped: filters.wrapped });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["tracks-streaming-history", query],
    queryFn: async () => getTracksStreamingHistory(query),
  });
}

export function useArtistsStreamingHistory(artistUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({
    artists: artistUris,
    wrapped: filters.wrapped,
  });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["artists-streaming-history", query],
    queryFn: async () => getArtistsStreamingHistory(query),
  });
}

export function useAlbumsStreamingHistory(albumUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({ albums: albumUris, wrapped: filters.wrapped });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["albums-streaming-history", query],
    queryFn: async () => getAlbumsStreamingHistory(query),
  });
}

export function useTracksStreamsByMonth(trackUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({ tracks: trackUris, wrapped: filters.wrapped });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["tracks-streams-by-month", query],
    queryFn: async () => getTracksStreamsByMonth(query),
  });
}

export function useArtistsStreamsByMonth(artistUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({
    artists: artistUris,
    wrapped: filters.wrapped,
  });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["artists-streams-by-month", query],
    queryFn: async () => getArtistsStreamsByMonth(query),
  });
}

export function useAlbumsStreamsByMonth(albumUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({ albums: albumUris, wrapped: filters.wrapped });
  return useQuery({
    ...defaultQueryOptions,
    queryKey: ["albums-streams-by-month", query],
    queryFn: async () => getAlbumsStreamsByMonth(query),
  });
}
