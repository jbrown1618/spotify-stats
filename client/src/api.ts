export interface Playlist {
  playlist_uri: string;
  playlist_name: string;
  playlist_image_url: string;
  playlist_owner: string;
  playlist_collaborative: boolean;
  playlist_liked_track_count: number;
  playlist_track_count: number;
}

export interface TrackDetails extends Album {
  track_duration_ms: number;
  track_explicit: boolean;
  track_isrc: string;
  track_liked: boolean;
  track_name: string;
  track_short_name: string;
  track_popularity: number;
  track_stream_count: number;
  track_uri: string;
  artist_names: string[];
}

export type Track = Pick<
  TrackDetails,
  | "track_uri"
  | "track_name"
  | "track_short_name"
  | "track_stream_count"
  | "album_image_url"
  | "album_release_date"
>;

export interface TrackRank {
  track_uri: string;
  track_rank: number;
  track_stream_count: number;
  as_of_date: string;
}

export interface Artist {
  artist_uri: string;
  artist_name: string;
  artist_followers: number;
  artist_liked_track_count: number;
  artist_popularity: number;
  artist_track_count: number;
  artist_image_url: string;
  artist_stream_count: number;
}

export interface ArtistRank {
  artist_uri: string;
  artist_rank: number;
  artist_stream_count: number;
  as_of_date: string;
}

export interface Album {
  album_uri: string;
  album_name: string;
  album_image_url: string;
  album_label: string;
  album_popularity: number;
  album_release_date: string;
  album_release_year: number;
  album_short_name: string;
  album_type: string;
  album_stream_count: number;
  album_track_count: number;
  album_liked_track_count: number;
}

export interface AlbumRank {
  album_uri: string;
  album_rank: number;
  album_stream_count: number;
  as_of_date: string;
}

export interface Label {
  label: string;
  track_count: number;
  total_track_count: number;
  liked_track_count: number;
  total_liked_track_count: number;
}

export interface Genre {
  genre: string;
  track_count: number;
  total_track_count: number;
  liked_track_count: number;
  total_liked_track_count: number;
}

export interface Producer {
  producer_name: string;
  producer_mbid: string;
  artist_uri: string | undefined;
  artist_image_url: string | undefined;
  liked_track_count: number;
  track_count: number;
  credit_types: string[];
}

export interface ReleaseYear {
  release_year: number;
  track_count: number;
  total_track_count: number;
  liked_track_count: number;
  total_liked_track_count: number;
}

export interface YearCounts {
  liked: number;
  total: number;
  year: number;
}

export interface ActiveFilters {
  liked?: boolean;
  tracks?: string[];
  labels?: string[];
  artists?: string[];
  albums?: string[];
  playlists?: string[];
  genres?: string[];
  years?: number[];
  wrapped?: string;
  producers?: string[];
}

export interface FilterOptions {
  artists: Record<string, Pick<Artist, "artist_uri" | "artist_name">>;
  albums: Record<string, Pick<Album, "album_uri" | "album_name">>;
  playlists: Record<string, Pick<Playlist, "playlist_uri" | "playlist_name">>;
  producers: Record<string, Pick<Producer, "producer_name" | "producer_mbid">>;
  labels: string[];
  genres: string[];
  years: number[];
}

export const defaultFilterOptions: FilterOptions = {
  artists: {},
  albums: {},
  playlists: {},
  producers: {},
  labels: [],
  genres: [],
  years: [],
};

export type StreamsByMonth = Record<
  string,
  Record<number, Record<number, number>>
>;

export async function getFilterOptions(): Promise<FilterOptions> {
  return sendRequest("/api/filters", "filter options");
}

export async function searchTracks(
  filters: ActiveFilters
): Promise<Record<string, Track>> {
  return sendRequest(`/api/tracks/search`, "tracks", filters);
}

export async function getTrack(
  uri: string,
  wrapped?: string
): Promise<TrackDetails> {
  return sendRequest(
    `/api/tracks/${uri}${wrapped ? "?wrapped=" + wrapped : ""}`,
    `track ${uri}`
  );
}

export async function getPlaylists(
  filters: Pick<ActiveFilters, "tracks">
): Promise<Record<string, Playlist>> {
  return sendRequest(`/api/playlists`, "playlists", filters);
}

export async function getArtists(
  filters: Pick<ActiveFilters, "tracks">
): Promise<Record<string, Artist>> {
  return sendRequest(`/api/artists`, "artists", filters);
}

export async function getAlbums(
  filters: Pick<ActiveFilters, "tracks">
): Promise<Record<string, Album>> {
  return sendRequest(`/api/albums`, "albums", filters);
}

export async function getLabels(
  filters: Pick<ActiveFilters, "tracks">
): Promise<Label[]> {
  return sendRequest(`/api/labels`, "labels", filters);
}

export async function getGenres(
  filters: Pick<ActiveFilters, "tracks">
): Promise<Genre[]> {
  return sendRequest(`/api/genres`, "genres", filters);
}

export async function getProducers(
  filters: Pick<ActiveFilters, "tracks">
): Promise<Record<string, Producer>> {
  return sendRequest(`/api/producers`, "producers", filters);
}

export async function getReleaseYears(
  filters: Pick<ActiveFilters, "tracks">
): Promise<ReleaseYear[]> {
  return sendRequest(`/api/release-years`, "release years", filters);
}

export async function getTracksStreamingHistory(
  filters: Pick<ActiveFilters, "tracks" | "wrapped">
): Promise<TrackRank[]> {
  return sendRequest(
    `/api/streams/tracks/history`,
    "tracks streaming history",
    filters
  );
}

export async function getArtistsStreamingHistory(
  filters: Pick<ActiveFilters, "artists" | "wrapped">
): Promise<ArtistRank[]> {
  return sendRequest(
    `/api/streams/artists/history`,
    "artists streaming history",
    filters
  );
}

export async function getAlbumsStreamingHistory(
  filters: Pick<ActiveFilters, "albums" | "wrapped">
): Promise<AlbumRank[]> {
  return sendRequest(
    `/api/streams/albums/history`,
    "albums streaming history",
    filters
  );
}

export async function getTracksStreamsByMonth(
  filters: Pick<ActiveFilters, "tracks" | "wrapped">
): Promise<StreamsByMonth> {
  return sendRequest(
    `/api/streams/tracks/months`,
    "track streams by month",
    filters
  );
}

export async function getArtistsStreamsByMonth(
  filters: Pick<ActiveFilters, "artists" | "wrapped">
): Promise<StreamsByMonth> {
  return sendRequest(
    `/api/streams/artists/months`,
    "artist streams by month",
    filters
  );
}

export async function getAlbumsStreamsByMonth(
  filters: Pick<ActiveFilters, "albums" | "wrapped">
): Promise<StreamsByMonth> {
  return sendRequest(
    `/api/streams/albums/months`,
    "album streams by month",
    filters
  );
}

async function sendRequest<T>(
  url: string,
  dataName: string,
  filters?: ActiveFilters
): Promise<T> {
  try {
    const headers = filters
      ? new Headers({ "Content-Type": "application/json" })
      : undefined;
    const res = await fetch(url, {
      method: filters ? "POST" : "GET",
      body: filters ? JSON.stringify(filters) : undefined,
      headers,
    });
    if (!res.ok)
      throw new Error(
        `Error fetching ${dataName}: ${res.status}: ${res.statusText}`
      );

    return await res.json();
  } catch (e: unknown) {
    const message =
      e instanceof Error ? e.message : `Error fetching ${dataName}`;
    throw new Error(message);
  }
}

const arrayKeys = [
  "artists",
  "albums",
  "playlists",
  "labels",
  "genres",
  "years",
  "tracks",
  "producers",
] as const;

export function toFiltersQuery(filters: ActiveFilters): string {
  const query = new URLSearchParams();
  for (const key of arrayKeys) {
    const value = filters[key];
    if (!value || value.length === 0) continue;
    const filterString = encodeURIComponent(JSON.stringify(value.sort()));
    query.append(key, filterString);
  }
  if (filters.liked) {
    query.append("liked", "true");
  }
  if (filters.wrapped) {
    query.append("wrapped", filters.wrapped);
  }
  return query.toString();
}

export function fromFiltersQuery(q: string): ActiveFilters {
  if (q.startsWith("?")) {
    q = q.substring(1);
  }
  const out: ActiveFilters = {};

  const pairs = q.split("&");
  for (const pair of pairs) {
    const [key, value] = pair.split("=");
    if (arrayKeys.includes(key as (typeof arrayKeys)[number])) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (out as any)[key] = JSON.parse(
        decodeURIComponent(decodeURIComponent(value))
      );
    } else if (key === "liked" || key === "wrapped") {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (out as any)[key] = decodeURIComponent(decodeURIComponent(value));
    }
  }

  return out;
}
