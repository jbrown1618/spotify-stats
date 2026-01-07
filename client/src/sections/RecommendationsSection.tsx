import { Select } from "@mantine/core";
import { useState } from "react";

import { Album, Artist } from "../api";
import { DisplayGrid } from "../design/DisplayGrid";
import { TextSkeleton } from "../design/TextSkeleton";
import { AlbumRow } from "../list-items/AlbumRow";
import { ArtistRow } from "../list-items/ArtistRow";
import { TrackRow } from "../list-items/TrackRow";
import {
  useAlbums,
  useArtists,
  useRecommendations,
  useTracks,
} from "../useApi";

export function RecommendationsSection() {
  const { data: recommendations, isLoading } = useRecommendations();
  const [selectedList, setSelectedList] = useState<string | null>(null);

  if (
    !isLoading &&
    (!recommendations || Object.keys(recommendations).length === 0)
  )
    return null;

  const listNames = recommendations ? Object.keys(recommendations) : [];
  const activeList = selectedList ?? listNames[0] ?? null;
  const activeRecommendation =
    activeList && recommendations ? recommendations[activeList] : null;

  if (isLoading) {
    return (
      <div>
        <h2>Recommendations</h2>
        <TextSkeleton style="regular" />
        <DisplayGrid
          loading={true}
          items={undefined}
          getKey={() => ""}
          renderRow={() => <></>}
        />
      </div>
    );
  }

  return (
    <div>
      <h2>Recommendations</h2>

      {listNames.length > 1 && (
        <Select
          label="Recommendation list"
          data={listNames}
          value={activeList}
          onChange={setSelectedList}
          style={{ maxWidth: 300, marginBottom: 16 }}
        />
      )}

      {activeRecommendation?.type === "track" && (
        <TrackRecommendations uris={activeRecommendation.uris} />
      )}

      {activeRecommendation?.type === "artist" && (
        <ArtistRecommendations uris={activeRecommendation.uris} />
      )}

      {activeRecommendation?.type === "album" && (
        <AlbumRecommendations uris={activeRecommendation.uris} />
      )}
    </div>
  );
}

function TrackRecommendations({ uris }: { uris: string[] }) {
  const { data: allTracks, isLoading } = useTracks({ tracks: uris });

  // Filter and sort tracks to match the order from recommendations
  const tracks = uris
    .map((uri) => allTracks?.[uri])
    .filter((t): t is NonNullable<typeof t> => !!t);

  return (
    <DisplayGrid
      loading={isLoading}
      items={tracks}
      getKey={(track) => track.track_uri}
      renderRow={(track) => <TrackRow trackUri={track.track_uri} />}
    />
  );
}

function ArtistRecommendations({ uris }: { uris: string[] }) {
  const { data: allArtists, isLoading } = useArtists({ artists: uris });

  // Filter and sort artists to match the order from recommendations
  const artists = uris
    .map((uri) => allArtists?.[uri])
    .filter((a): a is Artist => !!a);

  return (
    <DisplayGrid
      loading={isLoading}
      items={artists}
      getKey={(artist) => artist.artist_uri}
      renderRow={(artist) => <ArtistRow artist={artist} />}
    />
  );
}

function AlbumRecommendations({ uris }: { uris: string[] }) {
  const { data: allAlbums, isLoading } = useAlbums({ albums: uris });

  // Filter and sort albums to match the order from recommendations
  const albums = uris
    .map((uri) => allAlbums?.[uri])
    .filter((a): a is Album => !!a);

  return (
    <DisplayGrid
      loading={isLoading}
      items={albums}
      getKey={(album) => album.album_uri}
      renderRow={(album) => <AlbumRow album={album} />}
    />
  );
}
