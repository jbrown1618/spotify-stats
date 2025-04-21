import { Tabs } from "@mantine/core";

import { TrackStreamsLineChart } from "../charts/TracksLineChart";
import { TracksStreamingHistoryStack } from "../charts/TracksStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { TrackRow } from "../list-items/TrackRow";
import { trackSortOptions } from "../sorting";
import { useTracks } from "../useApi";
import { useFilters } from "../useFilters";

export function TracksSection() {
  const filters = useFilters();
  if (filters.tracks?.length === 1) return null;

  return (
    <div>
      <h2>Tracks</h2>

      <Tabs defaultValue="months">
        <Tabs.List>
          <Tabs.Tab value="months">Months</Tabs.Tab>
          <Tabs.Tab value="streams">Streams</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="streams">
          <TrackStreamsLineChart />
        </Tabs.Panel>

        <Tabs.Panel value="months">
          <TracksStreamingHistoryStack />
        </Tabs.Panel>
      </Tabs>

      <TracksDisplayGrid />
    </div>
  );
}

function TracksDisplayGrid() {
  const { data: tracks } = useTracks();
  return (
    <DisplayGrid
      items={tracks ? Object.values(tracks) : undefined}
      sortOptions={trackSortOptions}
      getKey={(track) => track.track_uri}
      renderRow={(track) => <TrackRow trackUri={track.track_uri} />}
    />
  );
}
