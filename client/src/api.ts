export interface Summary {
  filter_options: FilterOptions;
  playlists: Record<string, Playlist>;
  tracks: Record<string, Track>;
  artists: Record<string, Artist>;
  albums: Record<string, Album>;
  years: Record<string, YearCounts>;
  artists_by_track: Record<string, string[]>;
  artists_by_album: Record<string, string[]>;
  albums_by_artist: Record<string, string[]>;
  playlist_track_counts: Record<string, PlaylistTrackCount>;
  artist_track_counts: Record<string, ArtistTrackCount>;
  label_track_counts: Record<string, LabelTrackCount>;
  genre_track_counts: Record<string, GenreTrackCount>;
  track_rank_history: TrackRank[];
  artist_rank_history: ArtistRank[];
  album_rank_history: AlbumRank[];
  streams_by_month: Record<number, Record<number, number>>;
  track_streams_by_month: Record<
    string,
    Record<number, Record<number, number>>
  >;
  artist_streams_by_month: Record<
    string,
    Record<number, Record<number, number>>
  >;
  album_streams_by_month: Record<
    string,
    Record<number, Record<number, number>>
  >;
}

export interface Playlist {
  playlist_uri: string;
  playlist_name: string;
  playlist_image_url: string;
  playlist_owner: string;
  playlist_collaborative: boolean;
  playlist_liked_track_count: number;
  playlist_track_count: number;
}

export type PlaylistTrackCount = Pick<
  Playlist,
  | "playlist_uri"
  | "playlist_name"
  | "playlist_track_count"
  | "playlist_liked_track_count"
>;

export type ArtistTrackCount = Pick<
  Artist,
  | "artist_uri"
  | "artist_name"
  | "artist_track_count"
  | "artist_liked_track_count"
>;

export interface LabelTrackCount {
  label: string;
  label_track_count: number;
  label_liked_track_count: number;
}

export interface GenreTrackCount {
  genre: string;
  genre_track_count: number;
  genre_liked_track_count: number;
}

export interface Track extends Album {
  track_duration_ms: number;
  track_explicit: boolean;
  track_isrc: string;
  track_liked: boolean;
  track_name: string;
  track_short_name: string;
  track_popularity: number;
  track_rank: number;
  track_stream_count: number;
  track_uri: string;
}

export type BasicTrack = Pick<
  Track,
  | "track_uri"
  | "track_name"
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
  artist_rank: number;
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
  album_rank: number;
  album_image_url: string;
  album_label: string;
  album_popularity: number;
  album_release_date: string;
  album_release_year: number;
  album_short_name: string;
  album_type: string;
  album_stream_count: number;
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
}

export interface FilterOptions {
  artists: Record<string, Pick<Artist, "artist_uri" | "artist_name">>;
  albums: Record<string, Pick<Album, "album_uri" | "album_name">>;
  playlists: Record<string, Pick<Playlist, "playlist_uri" | "playlist_name">>;
  labels: string[];
  genres: string[];
  years: number[];
}

export const defaultFilterOptions: FilterOptions = {
  artists: {},
  albums: {},
  playlists: {},
  labels: [],
  genres: [],
  years: [],
};

export async function getSummary(query: string): Promise<Summary> {
  return sendRequest(`/api/summary?${query}`, "summary");
}

export async function getFilterOptions(): Promise<FilterOptions> {
  return sendRequest("/api/filters", "filter options");
}

export async function searchTracks(
  query: string
): Promise<Record<string, BasicTrack>> {
  return sendRequest(`/api/tracks/search?${query}`, "tracks");
}

export async function getTrack(uri: string): Promise<Track> {
  return sendRequest(`/api/tracks/${uri}`, `track ${uri}`);
}

export async function getPlaylists(
  query: string
): Promise<Record<string, Playlist>> {
  return sendRequest(`/api/playlists?${query}`, "playlists");
}

export async function getArtists(
  query: string
): Promise<Record<string, Artist>> {
  return sendRequest(`/api/artists?${query}`, "artists");
}

export async function getAlbums(query: string): Promise<Record<string, Album>> {
  return sendRequest(`/api/albums?${query}`, "albums");
}

export async function getLabels(query: string): Promise<Label[]> {
  return sendRequest(`/api/labels?${query}`, "labels");
}

export async function getGenres(query: string): Promise<Genre[]> {
  return sendRequest(`/api/genres?${query}`, "genres");
}

export async function getReleaseYears(query: string): Promise<ReleaseYear[]> {
  return sendRequest(`/api/release-years?${query}`, "release years");
}

export async function getTracksStreamingHistory(
  query: string
): Promise<TrackRank[]> {
  return sendRequest(
    `/api/streams/tracks/history?${query}`,
    "tracks streaming history"
  );
}

export async function getArtistsStreamingHistory(
  query: string
): Promise<ArtistRank[]> {
  return sendRequest(
    `/api/streams/artists/history?${query}`,
    "artists streaming history"
  );
}

export async function getAlbumsStreamingHistory(
  query: string
): Promise<AlbumRank[]> {
  return sendRequest(
    `/api/streams/albums/history?${query}`,
    "albums streaming history"
  );
}

export async function getTracksStreamsByMonth(
  query: string
): Promise<TrackRank[]> {
  return sendRequest(
    `/api/streams/tracks/months?${query}`,
    "track streams by month"
  );
}

export async function getArtistsStreamsByMonth(
  query: string
): Promise<ArtistRank[]> {
  return sendRequest(
    `/api/streams/artists/months?${query}`,
    "artist streams by month"
  );
}

export async function getAlbumsStreamsByMonth(
  query: string
): Promise<AlbumRank[]> {
  return sendRequest(
    `/api/streams/albums/months?${query}`,
    "album streams by month"
  );
}

async function sendRequest<T>(url: string, dataName: string): Promise<T> {
  try {
    const res = await fetch(url);
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
