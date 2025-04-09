import { Tabs } from "@mantine/core";

import {
  AlbumsRankLineChart,
  AlbumStreamsLineChart,
} from "../charts/AlbumsLineChart";
import { AlbumsStreamingHistoryStack } from "../charts/AlbumsStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { AlbumRow } from "../list-items/AlbumRow";
import { AlbumTile } from "../list-items/AlbumTile";
import { albumSortOptions } from "../sorting";
import { useAlbums } from "../useApi";
import { useFilters } from "../useFilters";

export function AlbumsSection() {
  const filters = useFilters();
  if (filters.albums?.length === 1) return null;

  return (
    <div>
      <h2>Albums</h2>

      <Tabs defaultValue="months">
        <Tabs.List>
          <Tabs.Tab value="months">Months</Tabs.Tab>
          <Tabs.Tab value="streams">Streams</Tabs.Tab>
          <Tabs.Tab value="rank">Rank</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="rank">
          <AlbumsRankLineChart />
        </Tabs.Panel>

        <Tabs.Panel value="streams">
          <AlbumStreamsLineChart />
        </Tabs.Panel>

        <Tabs.Panel value="months">
          <AlbumsStreamingHistoryStack />
        </Tabs.Panel>
      </Tabs>

      <AlbumsDisplayGrid />
    </div>
  );
}

function AlbumsDisplayGrid() {
  const { data: albums } = useAlbums();
  return (
    <DisplayGrid
      items={albums ? Object.values(albums) : undefined}
      sortOptions={albumSortOptions}
      getKey={(album) => album.album_uri}
      renderTile={(album) => <AlbumTile album={album} />}
      renderLargeTile={(album) => <AlbumTile large album={album} />}
      renderRow={(album) => <AlbumRow album={album} />}
    />
  );
}
