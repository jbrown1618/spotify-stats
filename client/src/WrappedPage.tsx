import { PropsWithChildren } from "react";
import { useParams } from "react-router";

import { DisplayGrid } from "./design/DisplayGrid";
import { Layout } from "./design/Layout";
import { AlbumRow } from "./list-items/AlbumRow";
import { ArtistRow } from "./list-items/ArtistRow";
import { TrackRow } from "./list-items/TrackRow";
import { compareValue, prioritize } from "./sorting";
import { useWrapped } from "./useWrapped";

export function WrappedPage({ children }: PropsWithChildren<unknown>) {
  return <Layout title="Wrapped">{children}</Layout>;
}

export function WrappedTimeFramePicker() {
  return <div>WrappedTimeFramePicker</div>;
}

export function WrappedForYear() {
  const { year } = useParams();
  const { data: wrapped } = useWrapped();

  return (
    <>
      <h2>Top Tracks of {year}</h2>
      <DisplayGrid
        items={wrapped ? Object.values(wrapped.tracks) : undefined}
        sortOptions={{
          "Top Tracks": prioritize(
            compareValue((t) => wrapped!.streams_by_track[t.track_uri]),
            compareValue((t) => t.track_stream_count)
          ),
        }}
        renderRow={(t) => (
          <TrackRow
            track={t}
            artists={wrapped!.artists}
            artists_by_track={wrapped!.artists_by_track}
          />
        )}
        getKey={(t) => t.track_uri}
      />

      <h2>Top Artists of {year}</h2>
      <DisplayGrid
        items={wrapped ? Object.values(wrapped.artists) : undefined}
        sortOptions={{
          "Top Tracks": prioritize(
            compareValue((t) => wrapped!.streams_by_artist[t.artist_uri]),
            compareValue((t) => t.artist_stream_count)
          ),
        }}
        renderRow={(t) => (
          <ArtistRow
            artist={t}
            albums={wrapped!.albums}
            album_by_artist={wrapped!.albums_by_artist}
          />
        )}
        getKey={(t) => t.artist_uri}
      />

      <h2>Top Albums of {year}</h2>
      <DisplayGrid
        items={wrapped ? Object.values(wrapped.albums) : undefined}
        sortOptions={{
          "Top Tracks": prioritize(
            compareValue((t) => wrapped!.streams_by_album[t.album_uri]),
            compareValue((t) => t.album_stream_count)
          ),
        }}
        renderRow={(t) => (
          <AlbumRow
            album={t}
            artists={wrapped!.artists}
            artists_by_album={wrapped!.artists_by_album}
          />
        )}
        getKey={(t) => t.album_uri}
      />
    </>
  );
}
