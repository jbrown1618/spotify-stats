import { ProducersBarChart } from "../charts/ProducersBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { ProducerPill } from "../list-items/ProducerPill";
import { PAGE_SIZE, useProducers } from "../useApi";

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
      getKey={(producer) => producer.producer_key}
      renderPill={(producer) => <ProducerPill producer={producer} />}
      
      isFetchingNextPage={isFetchingNextPage}
      onLoadMore={() => fetchNextPage()}
    />
  );
}
