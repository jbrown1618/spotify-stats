export interface Playlist {
  playlist_uri: string;
  playlist_name: string;
  playlist_image_url: string;
  playlist_owner: string;
  playlist_collaborative: boolean;
  playlist_liked_track_count: number;
  playlist_track_count: number;
}

export interface Track extends Album {
  track_duration_ms: number;
  track_explicit: boolean;
  track_isrc: string;
  track_liked: boolean;
  track_name: string;
  track_short_name: string;
  track_popularity: number;
  track_stream_count: number;
  track_last_played_at: string | null;
  track_uri: string;
  artist_names: string[];
  artist_uris: string[];
}

export interface TrackRank {
  track_uri: string;
  track_stream_count: number;
  as_of_date: string;
  track_short_name: string;
  track_name: string;
  album_image_url: string;
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
  artist_stream_count: number;
  as_of_date: string;
  artist_name: string;
  artist_image_url: string;
}

export interface ArtistCredit {
  recording_mbid: string;
  credit_type: string;
  credit_details: string | null;
  recording_title: string;
  spotify_track_uri: string | null;
  track_name: string | null;
  track_uri: string | null;
}

export interface ArtistRelationship {
  artist_mbid: string;
  artist_mb_name: string;
  artist_sort_name: string;
  relationship_type: string;
  relationship_direction: string;
  artist_uri: string | null;
  artist_name: string | null;
  artist_image_url: string | null;
}

export interface ArtistCreditsData {
  credits?: ArtistCredit[];
  aliases?: ArtistRelationship[];
  members?: Partial<ArtistWithMBData>[];
  groups?: ArtistRelationship[];
  subgroups?: ArtistRelationship[];
}

export interface ArtistWithMBData extends Artist {
  artist_mbid: string;
  artist_mb_name: string;
  artist_sort_name: string;
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
  album_stream_count: number;
  as_of_date: string;
  album_short_name: string;
  album_name: string;
  album_image_url: string;
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

export interface Credit {
  credit_type: string;
  credit_details: string | null;
  artist_mbid: string;
  artist_mb_name: string;
  artist_sort_name: string | null;
  artist_type: string | null;
  artist_uri: string | null;
  artist_name: string | null;
  artist_image_url: string | null;
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

export interface PaginationParams {
  limit: number;
  offset: number;
  sort: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
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

export interface StreamsByMonthResponse {
  streams: Record<string, Record<number, Record<number, number>>>;
  metadata: Record<string, Record<string, string>>;
}

export interface StreamShareMonth {
  month: string;
  category_key: string;
  category_name: string;
  stream_count: number;
  stream_share: number;
  sort_order: number;
}

export interface SpotifyAuthStatus {
  status: "ok" | "missing_cache" | "reauth_required" | "error";
}

export interface StreamDistributionBucket {
  entity_type: "track" | "album" | "artist";
  bucket: string;
  bucket_min: number;
  bucket_max: number | null;
  bucket_sort: number;
  item_count: number;
}

export interface ReleaseMonthCount {
  release_month: number;
  track_count: number;
  liked_track_count: number;
}

export interface TrackDiscoveryMonth {
  month: string;
  first_stream_count: number;
  retained_track_count: number;
}

export interface TotalStreamsMonth {
  month: string;
  stream_count: number;
}

export interface TrackVarietyMonth {
  month: string;
  total_stream_count: number;
  unique_track_count: number;
  effective_track_count: number;
  top_10_stream_share: number;
}

export interface WeekdayByWeekHeatmapCell {
  week_start: string;
  day_of_week: number;
  stream_count: number;
}

export interface MonthByYearHeatmapCell {
  year: number;
  month: number;
  stream_count: number;
}

export interface HourByWeekdayHeatmapCell {
  day_of_week: number;
  hour: number;
  stream_count: number;
}

export interface InsightsResponse {
  distributions: StreamDistributionBucket[];
  total_streams: TotalStreamsMonth[];
  release_months: ReleaseMonthCount[];
  discovery: TrackDiscoveryMonth[];
  variety: TrackVarietyMonth[];
  weekday_by_week: WeekdayByWeekHeatmapCell[];
  month_by_year: MonthByYearHeatmapCell[];
  hour_by_weekday: HourByWeekdayHeatmapCell[];
}

export async function getFilterOptions(): Promise<FilterOptions> {
  return sendRequest("/api/filters", "filter options");
}

export async function getSpotifyAuthStatus(): Promise<SpotifyAuthStatus> {
  return sendRequest("/api/spotify-auth/status", "Spotify auth status");
}

export async function getArtistCredits(
  artistUri: string
): Promise<ArtistCreditsData> {
  return sendRequest(
    `/api/artists/${artistUri}/credits`,
    `artist credits for ${artistUri}`
  );
}

export async function getTracks(
  filters: ActiveFilters & Partial<PaginationParams>
): Promise<PaginatedResponse<Track>> {
  return sendRequest(`/api/tracks`, "tracks", filters);
}

export async function getTrackCredits(uri: string): Promise<Credit[]> {
  return sendRequest(`/api/tracks/${uri}/credits`, `track credits for ${uri}`);
}

export async function getPlaylists(
  filters: ActiveFilters & Partial<PaginationParams>
): Promise<PaginatedResponse<Playlist>> {
  return sendRequest(`/api/playlists`, "playlists", filters);
}

export async function getArtists(
  filters: ActiveFilters & Partial<PaginationParams>
): Promise<PaginatedResponse<Artist>> {
  return sendRequest(`/api/artists`, "artists", filters);
}

export async function getAlbums(
  filters: ActiveFilters & Partial<PaginationParams>
): Promise<PaginatedResponse<Album>> {
  return sendRequest(`/api/albums`, "albums", filters);
}

export async function getLabels(
  filters: ActiveFilters & Partial<PaginationParams>
): Promise<PaginatedResponse<Label>> {
  return sendRequest(`/api/labels`, "labels", filters);
}

export async function getGenres(
  filters: ActiveFilters & Partial<PaginationParams>
): Promise<PaginatedResponse<Genre>> {
  return sendRequest(`/api/genres`, "genres", filters);
}

export async function getProducers(
  filters: ActiveFilters & Partial<PaginationParams>
): Promise<PaginatedResponse<Producer>> {
  return sendRequest(`/api/producers`, "producers", filters);
}

export async function getReleaseYears(
  filters: ActiveFilters & Partial<PaginationParams>
): Promise<PaginatedResponse<ReleaseYear>> {
  return sendRequest(`/api/release-years`, "release years", filters);
}

export async function getInsights(
  filters: ActiveFilters
): Promise<InsightsResponse> {
  return sendRequest(`/api/insights`, "insights", filters);
}

export async function getTracksStreamingHistory(
  filters: ActiveFilters & { n?: number }
): Promise<TrackRank[]> {
  return sendRequest(
    `/api/streams/tracks/history`,
    "tracks streaming history",
    filters
  );
}

export async function getArtistsStreamingHistory(
  filters: ActiveFilters & { n?: number }
): Promise<ArtistRank[]> {
  return sendRequest(
    `/api/streams/artists/history`,
    "artists streaming history",
    filters
  );
}

export async function getAlbumsStreamingHistory(
  filters: ActiveFilters & { n?: number }
): Promise<AlbumRank[]> {
  return sendRequest(
    `/api/streams/albums/history`,
    "albums streaming history",
    filters
  );
}

export async function getTracksStreamsByMonth(
  filters: ActiveFilters & { n?: number }
): Promise<StreamsByMonthResponse> {
  return sendRequest(
    `/api/streams/tracks/months`,
    "track streams by month",
    filters
  );
}

export async function getArtistsStreamsByMonth(
  filters: ActiveFilters & { n?: number }
): Promise<StreamsByMonthResponse> {
  return sendRequest(
    `/api/streams/artists/months`,
    "artist streams by month",
    filters
  );
}

export async function getArtistsStreamShareByMonth(
  filters: ActiveFilters & { n?: number }
): Promise<StreamShareMonth[]> {
  return sendRequest(
    `/api/streams/artists/share`,
    "artist stream share by month",
    filters
  );
}

export async function getAlbumsStreamsByMonth(
  filters: ActiveFilters & { n?: number }
): Promise<StreamsByMonthResponse> {
  return sendRequest(
    `/api/streams/albums/months`,
    "album streams by month",
    filters
  );
}

export async function getGenresStreamShareByMonth(
  filters: ActiveFilters & { n?: number }
): Promise<StreamShareMonth[]> {
  return sendRequest(
    `/api/streams/genres/share`,
    "genre stream share by month",
    filters
  );
}

export interface RecommendationList {
  type: "track" | "artist" | "album";
  uris: string[];
}

export type Recommendations = Record<string, RecommendationList>;

export async function getRecommendations(
  filters: ActiveFilters
): Promise<Recommendations> {
  return sendRequest(`/api/recommendations`, "recommendations", filters);
}

async function sendRequest<T>(
  url: string,
  dataName: string,
  params?: Record<string, unknown> | (ActiveFilters & Partial<PaginationParams>)
): Promise<T> {
  try {
    let fullUrl = url;
    if (params) {
      const query = toQueryString(params);
      if (query) fullUrl += `?${query}`;
    }
    const res = await fetch(fullUrl);
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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function toQueryString(params: Record<string, any>): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null) continue;
    if (Array.isArray(value)) {
      if (value.length === 0) continue;
      query.append(key, JSON.stringify(value));
    } else if (typeof value === "boolean") {
      if (value) query.append(key, "true");
    } else {
      query.append(key, String(value));
    }
  }
  return query.toString();
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
    const filterString = encodeURIComponent(JSON.stringify([...value].sort()));
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
