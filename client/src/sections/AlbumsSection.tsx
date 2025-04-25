import { Tabs } from "@mantine/core";
import { useEffect, useState } from "react";

import { AlbumStreamsLineChart } from "../charts/AlbumsLineChart";
import { AlbumsStreamingHistoryStack } from "../charts/AlbumsStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { AlbumRow } from "../list-items/AlbumRow";
import { AlbumTile } from "../list-items/AlbumTile";
import { albumSortOptions } from "../sorting";
import {
  useAlbums,
  useAlbumsStreamingHistory,
  useAlbumsStreamsByMonth,
} from "../useApi";
import { useFilters } from "../useFilters";

export function AlbumsSection() {
  const filters = useFilters();
  const { shouldRender: shouldRenderMonths } = useAlbumsStreamsByMonth();
  const { shouldRender: shouldRenderStreams } = useAlbumsStreamingHistory();
  const [activeTab, setActiveTab] = useState<string | null>(null);
  useEffect(() => {
    setActiveTab(shouldRenderMonths ? "months" : "streams");
  }, [shouldRenderMonths, shouldRenderStreams]);

  if (filters.albums?.length === 1) return null;

  return (
    <div>
      <h2>Albums</h2>

      <Tabs
        value={activeTab}
        onChange={setActiveTab}
        style={{
          display:
            shouldRenderMonths || shouldRenderStreams ? undefined : "none",
        }}
      >
        <Tabs.List>
          <Tabs.Tab
            value="months"
            style={{ display: shouldRenderMonths ? undefined : "none" }}
          >
            Months
          </Tabs.Tab>
          <Tabs.Tab
            value="streams"
            style={{ display: shouldRenderStreams ? undefined : "none" }}
          >
            Streams
          </Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel
          value="streams"
          style={{ display: shouldRenderStreams ? undefined : "none" }}
        >
          <AlbumStreamsLineChart />
        </Tabs.Panel>

        <Tabs.Panel
          value="months"
          style={{ display: shouldRenderMonths ? undefined : "none" }}
        >
          <AlbumsStreamingHistoryStack />
        </Tabs.Panel>
      </Tabs>

      <AlbumsDisplayGrid />
    </div>
  );
}

function AlbumsDisplayGrid() {
  const { data: albums, isLoading } = useAlbums();
  return (
    <DisplayGrid
      loading={isLoading}
      items={albums ? Object.values(albums) : undefined}
      sortOptions={albumSortOptions}
      getKey={(album) => album.album_uri}
      renderTile={(album) => <AlbumTile album={album} />}
      renderLargeTile={(album) => <AlbumTile large album={album} />}
      renderRow={(album) => <AlbumRow album={album} />}
    />
  );
}
