import { useQuery } from "@tanstack/react-query";

import {
  ActiveFilters,
  Album,
  AlbumRank,
  Artist,
  ArtistRank,
  FilterOptions,
  Genre,
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
  getTrack,
  getTracksStreamingHistory,
  getTracksStreamsByMonth,
  Label,
  Playlist,
  ReleaseYear,
  searchTracks,
  toFiltersQuery,
  Track,
  TrackDetails,
  TrackRank,
} from "./api";
import { useFilters } from "./useFilters";

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
    queryFn: async () => searchTracks(query),
  });
}

export function useTrack(uri: string) {
  return useQuery<TrackDetails>({
    ...defaultQueryOptions,
    queryKey: ["track", uri],
    queryFn: async () => getTrack(uri),
  });
}

export function usePlaylists() {
  const { data: tracks } = useTracks();
  const trackUris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: trackUris });
  return useQuery<Record<string, Playlist>>({
    ...defaultQueryOptions,
    queryKey: ["playlists", query],
    queryFn: async () => (trackUris.length === 0 ? {} : getPlaylists(query)),
  });
}

export function useArtists(filters?: ActiveFilters) {
  const { data: tracks } = useTracks(filters);
  const trackUris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: trackUris });
  return useQuery<Record<string, Artist>>({
    ...defaultQueryOptions,
    queryKey: ["artists", query],
    queryFn: async () => (trackUris.length === 0 ? {} : getArtists(query)),
  });
}

export function useAlbums(filters?: ActiveFilters) {
  const { data: tracks } = useTracks(filters);
  const trackUris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: trackUris });
  return useQuery<Record<string, Album>>({
    ...defaultQueryOptions,
    queryKey: ["albums", query],
    queryFn: async () => (trackUris.length === 0 ? {} : getAlbums(query)),
  });
}

export function useLabels() {
  const { data: tracks } = useTracks();
  const trackUris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: trackUris });
  return useQuery<Label[]>({
    ...defaultQueryOptions,
    queryKey: ["labels", query],
    queryFn: async () => (trackUris.length === 0 ? [] : getLabels(query)),
  });
}

export function useGenres() {
  const { data: tracks } = useTracks();
  const trackUris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: trackUris });
  return useQuery<Genre[]>({
    ...defaultQueryOptions,
    queryKey: ["genres", query],
    queryFn: async () => (trackUris.length === 0 ? [] : getGenres(query)),
  });
}

export function useReleaseYears() {
  const { data: tracks } = useTracks();
  const trackUris = tracks ? Object.keys(tracks) : [];
  const query = toFiltersQuery({ tracks: trackUris });
  return useQuery<ReleaseYear[]>({
    ...defaultQueryOptions,
    queryKey: ["release-years", query],
    queryFn: async () => (trackUris.length === 0 ? [] : getReleaseYears(query)),
  });
}

export function useTracksStreamingHistory(trackUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({ tracks: trackUris, wrapped: filters.wrapped });
  return useQuery<TrackRank[]>({
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
  return useQuery<ArtistRank[]>({
    ...defaultQueryOptions,
    queryKey: ["artists-streaming-history", query],
    queryFn: async () => getArtistsStreamingHistory(query),
  });
}

export function useAlbumsStreamingHistory(albumUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({ albums: albumUris, wrapped: filters.wrapped });
  return useQuery<AlbumRank[]>({
    ...defaultQueryOptions,
    queryKey: ["albums-streaming-history", query],
    queryFn: async () => getAlbumsStreamingHistory(query),
  });
}

export function useTracksStreamsByMonth(trackUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({ tracks: trackUris, wrapped: filters.wrapped });
  return useQuery<Record<string, Record<number, Record<number, number>>>>({
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
  return useQuery<Record<string, Record<number, Record<number, number>>>>({
    ...defaultQueryOptions,
    queryKey: ["artists-streams-by-month", query],
    queryFn: async () => getArtistsStreamsByMonth(query),
  });
}

export function useAlbumsStreamsByMonth(albumUris: string[]) {
  const filters = useFilters();
  const query = toFiltersQuery({ albums: albumUris, wrapped: filters.wrapped });
  return useQuery<Record<string, Record<number, Record<number, number>>>>({
    ...defaultQueryOptions,
    queryKey: ["albums-streams-by-month", query],
    queryFn: async () => getAlbumsStreamsByMonth(query),
  });
}
