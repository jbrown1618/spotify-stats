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
    queryFn: async () => searchTracks(filters ?? globalFilters),
  });
}

export function useTrack(uri: string) {
  return useQuery<TrackDetails>({
    ...defaultQueryOptions,
    queryKey: ["track", uri],
    queryFn: async () => getTrack(uri),
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

export function useTracksStreamingHistory(trackUris: string[]) {
  const { wrapped } = useFilters();
  const filters = { tracks: trackUris, wrapped };
  const query = toFiltersQuery(filters);
  return useQuery<TrackRank[]>({
    ...defaultQueryOptions,
    queryKey: ["tracks-streaming-history", query],
    queryFn: async () =>
      trackUris.length === 0 ? [] : getTracksStreamingHistory(filters),
  });
}

export function useArtistsStreamingHistory(artistUris: string[]) {
  const { wrapped } = useFilters();
  const filters = { artists: artistUris, wrapped };
  const query = toFiltersQuery(filters);
  return useQuery<ArtistRank[]>({
    ...defaultQueryOptions,
    queryKey: ["artists-streaming-history", query],
    queryFn: async () =>
      artistUris.length === 0 ? [] : getArtistsStreamingHistory(filters),
  });
}

export function useAlbumsStreamingHistory(albumUris: string[]) {
  const { wrapped } = useFilters();
  const filters = { albums: albumUris, wrapped };
  const query = toFiltersQuery(filters);
  return useQuery<AlbumRank[]>({
    ...defaultQueryOptions,
    queryKey: ["albums-streaming-history", query],
    queryFn: async () =>
      albumUris.length === 0 ? [] : getAlbumsStreamingHistory(filters),
  });
}

export function useTracksStreamsByMonth(trackUris: string[]) {
  const { wrapped } = useFilters();
  const filters = { tracks: trackUris, wrapped };
  const query = toFiltersQuery(filters);
  return useQuery<Record<string, Record<number, Record<number, number>>>>({
    ...defaultQueryOptions,
    queryKey: ["tracks-streams-by-month", query],
    queryFn: async () =>
      trackUris.length === 0 ? {} : getTracksStreamsByMonth(filters),
  });
}

export function useArtistsStreamsByMonth(artistUris: string[]) {
  const { wrapped } = useFilters();
  const filters = { artists: artistUris, wrapped };
  const query = toFiltersQuery(filters);
  return useQuery<Record<string, Record<number, Record<number, number>>>>({
    ...defaultQueryOptions,
    queryKey: ["artists-streams-by-month", query],
    queryFn: async () =>
      artistUris.length === 0 ? {} : getArtistsStreamsByMonth(filters),
  });
}

export function useAlbumsStreamsByMonth(albumUris: string[]) {
  const { wrapped } = useFilters();
  const filters = { albums: albumUris, wrapped };
  const query = toFiltersQuery(filters);
  return useQuery<Record<string, Record<number, Record<number, number>>>>({
    ...defaultQueryOptions,
    queryKey: ["albums-streams-by-month", query],
    queryFn: async () =>
      albumUris.length === 0 ? {} : getAlbumsStreamsByMonth(filters),
  });
}

function useTracksDependentQuery<T>(
  key: string,
  getValue: (filters: ActiveFilters) => Promise<T>,
  defaultValue: T,
  filters?: ActiveFilters
) {
  const globalFilters = useFilters();
  filters ??= globalFilters;
  const query = toFiltersQuery(filters);

  const { data: tracks } = useTracks(filters);
  const tracksFilter = { tracks: tracks ? Object.keys(tracks) : [] };

  return useQuery<T>({
    ...defaultQueryOptions,
    enabled: !!tracks,
    queryKey: [key, query],
    queryFn: async () =>
      tracksFilter.tracks.length === 0 ? defaultValue : getValue(tracksFilter),
  });
}
