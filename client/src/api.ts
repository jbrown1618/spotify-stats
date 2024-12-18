export interface Summary {
  filter_options: FilterOptions;
  playlists: Record<string, Playlist>;
  tracks: Record<string, Track>;
  artists: Record<string, Artist>;
  albums: Record<string, Album>;
  labels: string[];
  genres: string[];
  years: Record<string, YearCounts>;
  artists_by_track: Record<string, string[]>;
  artists_by_album: Record<string, string[]>;
  albums_by_artist: Record<string, string[]>;
  playlist_track_counts: Record<string, PlaylistTrackCount>;
  playlist_images: Record<string, string[]>;
  artist_track_counts: Record<string, ArtistTrackCount>;
  track_rank_history: TrackRank[];
  artist_rank_history: ArtistRank[];
  album_rank_history: AlbumRank[];
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

export interface Track extends Album {
  primary_artist_followers: number;
  primary_artist_has_page: boolean;
  primary_artist_image_url: string;
  primary_artist_liked_track_count: number;
  primary_artist_name: string;
  primary_artist_popularity: number;
  primary_artist_rank: number;
  primary_artist_track_count: number;
  primary_artist_uri: string;
  track_duration_ms: number;
  track_explicit: boolean;
  track_isrc: string;
  track_liked: boolean;
  track_name: string;
  track_popularity: number;
  track_rank: number;
  track_uri: string;
}

export interface TrackRank {
  track_uri: string;
  track_rank: number;
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
}

export interface ArtistRank {
  artist_uri: string;
  artist_rank: number;
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
  album_release_year: string;
  album_short_name: string;
  album_total_tracks: number;
  album_type: string;
}

export interface AlbumRank {
  album_uri: string;
  album_rank: number;
  as_of_date: string;
}

export interface Label {
  album_standardized_label: string;
}

export interface YearCounts {
  liked: number;
  total: number;
  year: string;
}

export interface ActiveFilters {
  liked?: boolean;
  labels?: string[];
  artists?: string[];
  albums?: string[];
  playlists?: string[];
  genres?: string[];
  years?: string[];
}

export interface FilterOptions {
  artists: Record<string, Pick<Artist, "artist_uri" | "artist_name">>;
  albums: Record<string, Pick<Album, "album_uri" | "album_name">>;
  playlists: Record<string, Pick<Playlist, "playlist_uri" | "playlist_name">>;
  labels: string[];
  genres: string[];
  years: string[];
}

export const defaultFilterOptions: FilterOptions = {
  artists: {},
  albums: {},
  playlists: {},
  labels: [],
  genres: [],
  years: [],
};

export async function getData(query: string): Promise<Summary> {
  try {
    const res = await fetch("/api/summary?" + query.toString());
    if (!res.ok)
      throw new Error(
        `Error fetching tracks summary: ${res.status}: ${res.statusText}`
      );

    return await res.json();
  } catch (e: unknown) {
    const message =
      e instanceof Error ? e.message : "Error fetching tracks summary";
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

export function filtersQuery(filters: ActiveFilters) {
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
  return query.toString();
}
