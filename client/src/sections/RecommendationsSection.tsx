import { RangeSlider } from "@mantine/core";
import { useState } from "react";

import { DisplayGrid } from "../design/DisplayGrid";
import { TrackRow } from "../list-items/TrackRow";
import { useRecommendationsInRange, useTracks } from "../useApi";
import { formatDate } from "../utils";
import styles from "./Sections.module.css";

export function RecommendationsSection() {
  const [range, setRange] = useState<[number, number]>([90, 100]);
  const [committedRange, setCommittedRange] = useState<[number, number]>(range);
  const {
    items: uris,
    total,
    isLoading,
    fetchNextPage,
    isFetchingNextPage,
  } = useRecommendationsInRange(committedRange[0], committedRange[1]);

  return (
    <div>
      <h2>Recommendations</h2>
      <RangeSlider
        label={(value) => `${value}th percentile`}
        labelAlwaysOn
        min={0}
        max={100}
        minRange={5}
        value={range}
        onChange={setRange}
        onChangeEnd={setCommittedRange}
        className={styles.recommendationCard}
      />
      <TrackRecommendations
        uris={uris}
        total={total}
        loading={isLoading}
        isFetchingNextPage={isFetchingNextPage}
        onLoadMore={fetchNextPage}
      />
    </div>
  );
}

function TrackRecommendations({
  uris,
  total,
  loading,
  isFetchingNextPage,
  onLoadMore,
}: {
  uris: string[];
  total: number;
  loading?: boolean;
  isFetchingNextPage?: boolean;
  onLoadMore?: () => void;
}) {
  const { items: allTracks, isLoading } = useTracks({ filters: { tracks: uris } });

  // Filter and sort tracks to match the order from recommendations
  const tracks = uris
    .map((uri) => allTracks?.find((t) => t.track_uri === uri))
    .filter((t): t is NonNullable<typeof t> => !!t);

  return (
    <DisplayGrid
      loading={loading || isLoading}
      items={tracks}
      total={total}
      getKey={(track) => track.track_uri}
      renderRow={(track) => (
        <TrackRow
          track={track}
          kpis={(t) => [
            {
              label: "Last Played",
              value: t.track_last_played_at
                ? formatDate(new Date(t.track_last_played_at))
                : "Never",
            },
          ]}
        />
      )}
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={onLoadMore}
    />
  );
}
