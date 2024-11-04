interface TracksSummary {
  tracks: Track[];
  artists: Artist[];
  albums: Album[];
  filters: Filters;
}

interface Track {}

interface Artist {}

interface Album {}

interface Filters {
  artists?: string[];
}

export async function getData(filters: Filters): Promise<TracksSummary> {
  const query = new URLSearchParams();
  for (const key of Object.keys(filters)) {
    const encoded = encodeURIComponent(
      JSON.stringify(filters[key as keyof Filters])
    );
    query.append(key, encoded);
  }

  try {
    const res = await fetch("/api/data?" + query.toString());
    if (!res.ok)
      throw new Error(
        `Error fetching tracks summary: ${res.status}: ${res.statusText}`
      );

    return await res.json();
  } catch (e: unknown) {
    throw new Error(
      e instanceof Error ? e.message : "Error fetching tracks summary"
    );
  }
}
