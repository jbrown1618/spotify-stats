import { useQuery } from "@tanstack/react-query";

interface TracksSummary {
  tracks: Track[];
  artists: Artist[];
  albums: Album[];
  filters: Filters;
}

interface Track {
  track_name: string;
}

interface Artist {
  artist_name: string;
}

interface Album {}

interface Filters {
  artists?: string[];
  albums?: string[];
  playlists?: string[];
}

export function useData(filters: Filters) {
  const query = filtersQuery(filters);
  return useQuery({
    queryKey: ["data", query],
    queryFn: async () => getData(query),
  });
}

async function getData(query: string): Promise<TracksSummary> {
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

function filtersQuery(filters: Filters) {
  const query = new URLSearchParams();
  const sortedKeys = Object.keys(filters).sort();
  for (const key of sortedKeys) {
    const value = filters[key as keyof Filters];
    if (!value || value.length === 0) continue;
    const filterString = encodeURIComponent(JSON.stringify(value.sort()));
    query.append(key, filterString);
  }
  return query.toString();
}
