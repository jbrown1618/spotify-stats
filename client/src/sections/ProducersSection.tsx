import { Pill } from "@mantine/core";

import { Producer } from "../api";
import { ProducersBarChart } from "../charts/ProducersBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { useProducers, PAGE_SIZE } from "../useApi";
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
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    useProducers({ sort: "Most tracks", limit: PAGE_SIZE });

  return (
    <DisplayGrid
      loading={isLoading}
      items={items}
      total={total}
      getKey={(producer) => producer.producer_mbid}
      renderPill={(producer) => <ProducerPill producer={producer} />}
      
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
