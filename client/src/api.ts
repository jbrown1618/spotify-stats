export interface Summary {
  tracks: Track[];
  artists: Artist[];
  albums: Album[];
  filters: ActiveFilters;
  filter_options: FilterOptions;
}

export interface Track {
  track_name: string;
}

export interface Artist {
  artist_name: string;
}

export interface Album {}

export interface ActiveFilters {
  artists?: string[];
  albums?: string[];
  playlists?: string[];
}

export interface FilterOptions {
  artists: Record<string, string>;
}

export async function getData(query: string): Promise<Summary> {
  try {
    const res = await fetch("/api/data?" + query.toString());
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

export function filtersQuery(filters: ActiveFilters) {
  const query = new URLSearchParams();
  const sortedKeys = Object.keys(filters).sort();
  for (const key of sortedKeys) {
    const value = filters[key as keyof ActiveFilters];
    if (!value || value.length === 0) continue;
    const filterString = encodeURIComponent(JSON.stringify(value.sort()));
    query.append(key, filterString);
  }
  return query.toString();
}
