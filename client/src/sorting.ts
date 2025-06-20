import { Album, Artist, Track } from "./api";

type Comparator<T> = (a: T, b: T) => number;

export type SortOptions<T> = Record<string, Comparator<T>>;

function reverse<T>(comparator: Comparator<T>): Comparator<T> {
  return (a, b) => -1 * comparator(a, b);
}

function prioritize<T>(...comparators: Comparator<T>[]): Comparator<T> {
  return (a: T, b: T) => {
    for (const compare of comparators) {
      const result = compare(a, b);
      if (result !== 0) return result;
    }
    return 0;
  };
}

function compareValue<T>(cb: (val: T) => string | number) {
  return (a: T, b: T) => {
    const aVal = cb(a);
    const bVal = cb(b);

    if (aVal < bVal) return 1;
    if (aVal > bVal) return -1;
    return 0;
  };
}

const alphabeticalTracks: Comparator<Track> = prioritize(
  reverse(compareValue((t) => t.track_name)),
  compareValue((t) => t.track_uri)
);

export const mostStreamedTracks: Comparator<Track> = prioritize(
  compareValue((t) => t.track_stream_count),
  alphabeticalTracks
);

const mostRecentTracks: Comparator<Track> = prioritize(
  compareValue((a) => new Date(a.album_release_date).getTime()),
  alphabeticalTracks
);

const alphabeticalAlbums: Comparator<Album> = prioritize(
  reverse(compareValue((t) => t.album_name)),
  compareValue((t) => t.album_uri)
);

export const mostStreamedAlbums: Comparator<Album> = prioritize(
  compareValue((a) => a.album_stream_count),
  alphabeticalAlbums
);

const mostRecentAlbums: Comparator<Album> = prioritize(
  compareValue((a) => new Date(a.album_release_date).getTime()),
  alphabeticalAlbums
);

export const mostLikedAlbums: Comparator<Album> = prioritize(
  compareValue((a) => a.album_liked_track_count),
  compareValue((a) => a.album_track_count),
  mostStreamedAlbums
);

const alphabeticalArtists: Comparator<Artist> = prioritize(
  reverse(compareValue((t) => t.artist_name)),
  compareValue((t) => t.artist_uri)
);

export const mostStreamedArtists: Comparator<Artist> = prioritize(
  compareValue((a) => a.artist_stream_count),
  compareValue((a) => a.artist_popularity),
  compareValue((a) => a.artist_followers),
  alphabeticalArtists
);

export const mostLikedArtists: Comparator<Artist> = prioritize(
  compareValue((a) => a.artist_liked_track_count),
  compareValue((a) => a.artist_track_count),
  mostStreamedArtists
);

export const trackSortOptions: Record<string, Comparator<Track>> = {
  "Most streamed": mostStreamedTracks,
  "Least streamed": reverse(mostStreamedTracks),
  Newest: prioritize(mostRecentTracks, alphabeticalTracks),
  Oldest: reverse(prioritize(mostRecentTracks, alphabeticalTracks)),
  Alphabetical: alphabeticalTracks,
};

export const albumSortOptions: Record<string, Comparator<Album>> = {
  "Most streamed": mostStreamedAlbums,
  "Least streamed": reverse(mostStreamedAlbums),
  Newest: mostRecentAlbums,
  Oldest: reverse(mostRecentAlbums),
  Alphabetical: alphabeticalAlbums,
};

export const artistSortOptions: Record<string, Comparator<Artist>> = {
  "Most streamed": mostStreamedArtists,
  "Least streamed": reverse(mostStreamedArtists),
  Alphabetical: alphabeticalArtists,
};
