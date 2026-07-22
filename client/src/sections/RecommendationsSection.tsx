import { RangeSlider, Text } from "@mantine/core";
import { useState } from "react";

import { DisplayGrid } from "../design/DisplayGrid";
import { TextSkeleton } from "../design/TextSkeleton";
import { TrackRow } from "../list-items/TrackRow";
import {
  DEFAULT_RECOMMENDATION_PERCENTILE_RANGE,
  useRecommendations,
  useTracks,
} from "../useApi";
import { formatDate } from "../utils";
import styles from "./Sections.module.css";

export function RecommendationsSection() {
  const [sliderRange, setSliderRange] = useState<[number, number]>([
    ...DEFAULT_RECOMMENDATION_PERCENTILE_RANGE,
  ]);
  const [queryRange, setQueryRange] = useState<[number, number]>(sliderRange);
  const { data: recommendations, isLoading } = useRecommendations(queryRange);

  if (isLoading) {
    return (
      <div>
        <h2>Recommendations</h2>
        <RecommendationRangeSlider
          value={sliderRange}
          onChange={setSliderRange}
          onChangeEnd={setQueryRange}
        />
        <TextSkeleton style="regular" />
        <DisplayGrid
          loading={true}
          items={undefined}
          getKey={() => ""}
          renderRow={() => <></>}
        />
      </div>
    );
  }

  return (
    <div>
      <h2>Recommendations</h2>

      <RecommendationRangeSlider
        value={sliderRange}
        onChange={setSliderRange}
        onChangeEnd={setQueryRange}
      />

      <RecommendationTracks uris={recommendations?.uris ?? []} />
    </div>
  );
}

function RecommendationRangeSlider({
  value,
  onChange,
  onChangeEnd,
}: {
  value: [number, number];
  onChange: (value: [number, number]) => void;
  onChangeEnd: (value: [number, number]) => void;
}) {
  return (
    <div className={styles.recommendationCard}>
      <Text size="sm" fw={500}>
        Stream count percentile range
      </Text>
      <Text size="sm" c="dimmed" mb="md">
        Showing tracks in the {value[0]}-{value[1]} percentile, least recently
        streamed first.
      </Text>
      <RangeSlider
        min={0}
        max={100}
        step={1}
        value={value}
        onChange={onChange}
        onChangeEnd={onChangeEnd}
        marks={[
          { value: 0, label: "0" },
          { value: 50, label: "50" },
          { value: 100, label: "100" },
        ]}
      />
    </div>
  );
}

function RecommendationTracks({ uris }: { uris: string[] }) {
  if (uris.length === 0) {
    return (
      <DisplayGrid
        loading={false}
        items={[]}
        getKey={() => ""}
        renderRow={() => <></>}
      />
    );
  }

  return <TrackRecommendations uris={uris} />;
}

function TrackRecommendations({ uris }: { uris: string[] }) {
  const { items: allTracks, isLoading } = useTracks({
    filters: { tracks: uris },
  });

  const tracks = uris
    .map((uri) => allTracks?.find((t) => t.track_uri === uri))
    .filter((t): t is NonNullable<typeof t> => !!t);

  return (
    <DisplayGrid
      loading={isLoading}
      items={tracks}
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
    />
  );
}
