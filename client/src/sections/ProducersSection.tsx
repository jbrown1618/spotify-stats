import { ProducersBarChart } from "../charts/ProducersBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { ProducerPill } from "../list-items/ProducerPill";
import { PAGE_SIZE, useProducers } from "../useApi";
import { SectionHeading } from "./SectionHeading";

export function ProducersSection() {
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    useProducers({ sort: "Most tracks", limit: PAGE_SIZE });

  return (
    <div>
      <SectionHeading title="Producers" total={total} />
      <ProducersBarChart />
      <DisplayGrid
        loading={isLoading}
        items={items}
        total={total}
        getKey={(producer) => producer.producer_key}
        renderPill={(producer) => <ProducerPill producer={producer} />}
        isFetchingNextPage={isFetchingNextPage}
        onLoadMore={() => fetchNextPage()}
      />
    </div>
  );
}
