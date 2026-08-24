import { PillWithAvatar } from "../design/PillDesign";
import { useSetFilters } from "../useFilters";

interface ProducerPillProps {
  producer_key: string;
  producer_name: string;
  artist_image_url?: string | null;
}

export function ProducerPill({ producer }: { producer: ProducerPillProps }) {
  const setFilters = useSetFilters();

  return (
    <PillWithAvatar
      imageHref={producer.artist_image_url ?? ""}
      onClick={() => setFilters({ producers: [producer.producer_key] })}
    >
      {producer.producer_name}
    </PillWithAvatar>
  );
}
