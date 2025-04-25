import { Tabs } from "@mantine/core";
import { useEffect, useState } from "react";

import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { TrackRow } from "../list-items/TrackRow";
import { trackSortOptions } from "../sorting";
import {
  useTracks,
  useTracksStreamingHistory,
  useTracksStreamsByMonth,
} from "../useApi";
import { useFilters } from "../useFilters";

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
  const { data: tracks, isLoading } = useTracks();
  return (
    <DisplayGrid
      loading={isLoading}
      items={tracks ? Object.values(tracks) : undefined}
      sortOptions={trackSortOptions}
      getKey={(track) => track.track_uri}
      renderRow={(track) => <TrackRow trackUri={track.track_uri} />}
    />
  );
}
