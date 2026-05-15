import { Tabs } from "@mantine/core";
import { useEffect, useState } from "react";

import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { TrackRow } from "../list-items/TrackRow";
import {
  usePaginatedTracks,
  useTracksStreamingHistory,
  useTracksStreamsByMonth,
} from "../useApi";
import { useFilters } from "../useFilters";

const trackSortOptions = [
  "Most streams",
  "Least streams",
  "Recently played",
  "Least recently played",
  "Newest",
  "Oldest",
  "Alphabetical",
];

export function TracksSection() {
  const filters = useFilters();
  const { shouldRender: shouldRenderMonths } = useTracksStreamsByMonth();
  const { shouldRender: shouldRenderStreams } = useTracksStreamingHistory();
  const [activeTab, setActiveTab] = useState<string | null>(null);
  useEffect(() => {
    setActiveTab(shouldRenderMonths ? "months" : "streams");
  }, [shouldRenderMonths, shouldRenderStreams]);
  if (filters.tracks?.length === 1) return null;

  return (
    <div>
      <h2>Tracks</h2>

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
          <TrackStreamsLineChart />
        </Tabs.Panel>

        <Tabs.Panel
          value="months"
          style={{ display: shouldRenderMonths ? undefined : "none" }}
        >
          <TracksStreamingHistoryStack />
        </Tabs.Panel>
      </Tabs>

      <TracksDisplayGrid />
    </div>
  );
}

function TracksDisplayGrid() {
  const [sort, setSort] = useState("Most streams");
  const { data, isLoading, hasNextPage, fetchNextPage, isFetchingNextPage } =
    usePaginatedTracks(sort);

  const items = data?.pages.flatMap((p) => p.items);
  const total = data?.pages[0]?.total ?? 0;

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      sortOptions={trackSortOptions}
      sort={sort}
      onSortChange={setSort}
      getKey={(track) => track.track_uri}
      renderRow={(track) => <TrackRow trackUri={track.track_uri} />}
      hasNextPage={hasNextPage}
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}
