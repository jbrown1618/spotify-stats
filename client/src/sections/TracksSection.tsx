import { Tabs } from "@mantine/core";
import { ReactNode, useEffect, useState } from "react";

import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { TrackRow } from "../list-items/TrackRow";
import {
  PAGE_SIZE,
  useTracks,
  useTracksStreamingHistory,
  useTracksStreamsByMonth,
} from "../useApi";
import { SectionHeading } from "./SectionHeading";

const trackSortOptions = [
  "Most streams",
  "Least streams",
  "Recently played",
  "Least recently played",
  "Newest",
  "Oldest",
  "Alphabetical",
];

interface TracksSectionProps {
  overview?: ReactNode;
}

export function TracksSection({ overview }: TracksSectionProps) {
  const { shouldRender: shouldRenderMonths } = useTracksStreamsByMonth();
  const { shouldRender: shouldRenderStreams } = useTracksStreamingHistory();
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [sort, setSort] = useState("Most streams");
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    useTracks({ sort, limit: PAGE_SIZE });

  useEffect(() => {
    setActiveTab(shouldRenderMonths ? "months" : "streams");
  }, [shouldRenderMonths, shouldRenderStreams]);

  return (
    <div>
      {overview}
      <SectionHeading title="Tracks" total={total} />

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

      <DisplayGrid
        loading={isLoading}
        items={items}
        total={total}
        sortOptions={trackSortOptions}
        sort={sort}
        onSortChange={setSort}
        getKey={(track) => track.track_uri}
        renderRow={(track) => <TrackRow track={track} />}
        isFetchingNextPage={isFetchingNextPage}
        onLoadMore={() => fetchNextPage()}
      />
    </div>
  );
}
