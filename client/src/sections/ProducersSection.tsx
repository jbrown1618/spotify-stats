import { Pill } from "@mantine/core";

import { Producer } from "../api";
import { ProducersBarChart } from "../charts/ProducersBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { useProducers } from "../useApi";
import { useSetFilters } from "../useFilters";

export function ProducersSection() {
  return (
    <div>
      <h2>Producers</h2>
      <ProducersBarChart />
      <ProducersDisplayGrid />
    </div>
  );
}

function ProducersDisplayGrid() {
  const { data: producers, isLoading } = useProducers();
  return (
    <DisplayGrid
      loading={isLoading}
      items={
        producers
          ? Object.values(producers).sort(
              (a, b) => b.liked_track_count - a.liked_track_count
            )
          : undefined
      }
      getKey={(producer) => producer.producer_mbid}
      renderPill={(producer) => <ProducerPill producer={producer} />}
    />
  );
}

function ProducerPill({ producer }: { producer: Producer }) {
  const setFilters = useSetFilters();
  return (
    <Pill
      bg="gray"
      size="lg"
      style={{ cursor: "pointer" }}
      onClick={() => setFilters({ producers: [producer.producer_mbid] })}
    >
      {producer.producer_name}
    </Pill>
  );
}
