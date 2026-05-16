import { Tabs } from "@mantine/core";
import { useEffect, useState } from "react";

import { AlbumsBarChart } from "../charts/AlbumsBarChart";
import { AlbumStreamsLineChart } from "../charts/AlbumsLineChart";
import { AlbumsStreamingHistoryStack } from "../charts/AlbumsStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { AlbumRow } from "../list-items/AlbumRow";
import { AlbumTile } from "../list-items/AlbumTile";
import {
  useAlbums,
  useAlbumsStreamingHistory,
  useAlbumsStreamsByMonth,
  PAGE_SIZE,
} from "../useApi";

const albumSortOptions = [
  "Most streams",
  "Least streams",
  "Newest",
  "Oldest",
  "Alphabetical",
];

export function AlbumsSection() {
  const { shouldRender: shouldRenderMonths } = useAlbumsStreamsByMonth();
  const { shouldRender: shouldRenderStreams } = useAlbumsStreamingHistory();

  const [activeTab, setActiveTab] = useState<string | null>(null);
  useEffect(() => {
    setActiveTab(
      shouldRenderMonths ? "months" : shouldRenderStreams ? "streams" : "counts"
    );
  }, [shouldRenderMonths, shouldRenderStreams]);

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
          <Tabs.Tab value="count">
            Count
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

        <Tabs.Panel value="count">
          <AlbumsBarChart />
        </Tabs.Panel>
      </Tabs>

      <AlbumsDisplayGrid />
    </div>
  );
}

function AlbumsDisplayGrid() {
  const [sort, setSort] = useState("Most streams");
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    useAlbums({ sort, limit: PAGE_SIZE });

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      sortOptions={albumSortOptions}
      sort={sort}
      onSortChange={setSort}
      getKey={(album) => album.album_uri}
      renderTile={(album) => <AlbumTile album={album} />}
      renderLargeTile={(album) => <AlbumTile large album={album} />}
      renderRow={(album) => <AlbumRow album={album} />}
      
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}
