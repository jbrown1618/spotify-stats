import { Pill } from "@mantine/core";

import { Producer } from "../api";
import { ProducersBarChart } from "../charts/ProducersBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { usePaginatedProducers } from "../useApi";
import { useSetFilters } from "../useFilters";
import styles from "./Sections.module.css";

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
  const { data, isLoading, hasNextPage, fetchNextPage, isFetchingNextPage } =
    usePaginatedProducers();

  const items = data?.pages.flatMap((p) => p.items);
  const total = data?.pages[0]?.total ?? 0;

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      getKey={(producer) => producer.producer_mbid}
      renderPill={(producer) => <ProducerPill producer={producer} />}
      hasNextPage={hasNextPage}
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}

function ProducerPill({ producer }: { producer: Producer }) {
  const setFilters = useSetFilters();
  return (
    <Pill
      bg="gray"
      size="lg"
      className={styles.clickable}
      onClick={() => setFilters({ producers: [producer.producer_mbid] })}
    >
      {producer.producer_name}
    </Pill>
  );
}
