import { Anchor } from "@mantine/core";

import { ActiveFilters, toFiltersQuery } from "../api";
import { useSetFilters } from "../useFilters";
import styles from "./StreamingHistoryItem.module.css";

export function StreamingHistoryItem({
  filters,
  imageUrl,
  name,
}: {
  filters: ActiveFilters;
  imageUrl: string;
  name: string;
}) {
  const setFilters = useSetFilters();

  return (
    <h4 className={styles.itemHeading}>
      <Anchor
        className={styles.itemLink}
        href={`?${toFiltersQuery(filters)}`}
        underline="hover"
        onClick={(event) => {
          if (
            event.button !== 0 ||
            event.metaKey ||
            event.ctrlKey ||
            event.shiftKey ||
            event.altKey
          ) {
            return;
          }

          event.preventDefault();
          setFilters(filters);
        }}
      >
        <img className={styles.itemImage} src={imageUrl} alt="" />
        <span className={styles.itemName}>{name}</span>
      </Anchor>
    </h4>
  );
}
