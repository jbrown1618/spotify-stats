import { Tabs } from "@mantine/core";
import { useEffect, useState } from "react";

import { ArtistsBarChart } from "../charts/ArtistsBarChart";
import { ArtistStreamsLineChart } from "../charts/ArtistsLineChart";
import { ArtistsStreamingHistoryStack } from "../charts/ArtistsStreamingHistoryStack";
import { StreamShareAreaChart } from "../charts/StreamShareAreaChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { ArtistRow } from "../list-items/ArtistRow";
import { ArtistTile } from "../list-items/ArtistTile";
import {
  PAGE_SIZE,
  useArtists,
  useArtistsStreamingHistory,
  useArtistsStreamsByMonth,
  useArtistsStreamShareByMonth,
} from "../useApi";

const artistSortOptions = ["Most streams", "Least streams", "Alphabetical"];

export function ArtistsSection() {
  const { shouldRender: shouldRenderMonths } = useArtistsStreamsByMonth();
  const { shouldRender: shouldRenderStreams } = useArtistsStreamingHistory();
  const {
    data: shareRows,
    shouldRender: shouldRenderShare,
  } = useArtistsStreamShareByMonth();

  const [activeTab, setActiveTab] = useState<string | null>(null);
  useEffect(() => {
    setActiveTab(
      shouldRenderShare
        ? "share"
        : shouldRenderMonths ? "months" : shouldRenderStreams ? "streams" : "counts"
    );
  }, [shouldRenderMonths, shouldRenderShare, shouldRenderStreams]);

  return (
    <div>
      <h2>Artists</h2>

      <Tabs
        value={activeTab}
        onChange={setActiveTab}
        style={{
          display:
            shouldRenderShare || shouldRenderMonths || shouldRenderStreams
              ? undefined
              : "none",
        }}
      >
        <Tabs.List>
          <Tabs.Tab
            value="share"
            style={{ display: shouldRenderShare ? undefined : "none" }}
          >
            Share
          </Tabs.Tab>
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
          value="share"
          style={{ display: shouldRenderShare ? undefined : "none" }}
        >
          <StreamShareAreaChart
            rows={shareRows ?? []}
            title="Artist stream share over time"
            description="Monthly share for your current top 10 artists, with all other artists grouped as Other."
          />
        </Tabs.Panel>

        <Tabs.Panel
          value="streams"
          style={{ display: shouldRenderStreams ? undefined : "none" }}
        >
          <ArtistStreamsLineChart />
        </Tabs.Panel>

        <Tabs.Panel value="count">
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
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
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
      
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}
