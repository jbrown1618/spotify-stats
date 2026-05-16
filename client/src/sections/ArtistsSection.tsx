import { Tabs } from "@mantine/core";
import { useEffect, useState } from "react";

import { ArtistsBarChart } from "../charts/ArtistsBarChart";
import { ArtistStreamsLineChart } from "../charts/ArtistsLineChart";
import { ArtistsStreamingHistoryStack } from "../charts/ArtistsStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { ArtistRow } from "../list-items/ArtistRow";
import { ArtistTile } from "../list-items/ArtistTile";
import {
  useArtists,
  useArtistsStreamingHistory,
  useArtistsStreamsByMonth,
  PAGE_SIZE,
} from "../useApi";
import { useFilters } from "../useFilters";

const artistSortOptions = ["Most streams", "Least streams", "Alphabetical"];

export function ArtistsSection() {
  const filters = useFilters();
  const { items: artists } = useArtists();
  const { shouldRender: shouldRenderMonths } = useArtistsStreamsByMonth();
  const { shouldRender: shouldRenderStreams } = useArtistsStreamingHistory();
  const shouldRenderCounts = artists && artists.length >= 3;

  const [activeTab, setActiveTab] = useState<string | null>(null);
  useEffect(() => {
    setActiveTab(
      shouldRenderMonths ? "months" : shouldRenderStreams ? "streams" : "counts"
    );
  }, [shouldRenderMonths, shouldRenderStreams, shouldRenderCounts]);

  if (filters.artists?.length === 1) return null;

  return (
    <div>
      <h2>Artists</h2>

      <Tabs
        value={activeTab}
        onChange={setActiveTab}
        style={{
          display:
            shouldRenderCounts || shouldRenderMonths || shouldRenderStreams
              ? undefined
              : "none",
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
          <Tabs.Tab
            value="count"
            style={{ display: shouldRenderCounts ? undefined : "none" }}
          >
            Count
          </Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel
          value="streams"
          style={{ display: shouldRenderStreams ? undefined : "none" }}
        >
          <ArtistStreamsLineChart />
        </Tabs.Panel>

        <Tabs.Panel
          value="count"
          style={{ display: shouldRenderCounts ? undefined : "none" }}
        >
          <ArtistsBarChart />
        </Tabs.Panel>

        <Tabs.Panel
          value="months"
          style={{ display: shouldRenderMonths ? undefined : "none" }}
        >
          <ArtistsStreamingHistoryStack />
        </Tabs.Panel>
      </Tabs>

      <ArtistsDisplayGrid />
    </div>
  );
}

function ArtistsDisplayGrid() {
  const [sort, setSort] = useState("Most streams");
  const { items, total, isLoading, hasNextPage, fetchNextPage, isFetchingNextPage } =
    useArtists({ sort, limit: PAGE_SIZE });

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      sortOptions={artistSortOptions}
      sort={sort}
      onSortChange={setSort}
      getKey={(artist) => artist.artist_uri}
      renderTile={(artist) => <ArtistTile artist={artist} />}
      renderLargeTile={(artist) => <ArtistTile large artist={artist} />}
      renderRow={(artist) => <ArtistRow artist={artist} />}
      hasNextPage={hasNextPage}
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}
