export interface Summary {
  playlists: Record<string, Playlist>;
  tracks: Record<string, Track>;
  artists: Record<string, Artist>;
  albums: Record<string, Album>;
  labels: string[];
  genres: string[];
  filter_options: FilterOptions;
}

export interface Playlist {
  playlist_uri: string;
  playlist_name: string;
}

export interface Track {
  track_uri: string;
  track_name: string;
}

export interface Artist {
  artist_uri: string;
  artist_name: string;
}

export interface Album {
  album_uri: string;
  album_name: string;
}

export interface Label {
  album_standardized_label: string;
}

export interface ActiveFilters {
  liked?: boolean;
  labels?: string[];
  artists?: string[];
  albums?: string[];
  playlists?: string[];
  genres?: string[];
}

export interface FilterOptions {
  artists: Record<string, Pick<Artist, "artist_uri" | "artist_name">>;
  albums: Record<string, Pick<Album, "album_uri" | "album_name">>;
  playlists: Record<string, Pick<Playlist, "playlist_uri" | "playlist_name">>;
  labels: string[];
  genres: string[];
}

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
