import {
  Button,
  SegmentedControl,
  SegmentedControlItem,
  Select,
  Text,
} from "@mantine/core";
import {
  IconGridDots,
  IconLayoutGridFilled,
  IconList,
  IconMinus,
  IconPill,
  IconPlus,
} from "@tabler/icons-react";
import clsx from "clsx";
import { useRef, useState } from "react";

import { SortOptions } from "../sorting";
import styles from "./DisplayGrid.module.css";
import { LargeTileSkeleton } from "./LargeTileDesign";
import { PillSkeleton } from "./PillDesign";
import { RowSkeleton } from "./RowDesign";
import { TileSkeleton } from "./TileDesign";

interface DisplayGridProps<T> {
  loading: boolean;
  items: T[] | undefined;
  total?: number;
  sortOptions?: SortOptions<T>;
  serverSortOptions?: string[];
  serverSort?: string;
  onServerSortChange?: (sort: string) => void;
  getKey: (item: T) => string;
  renderTile?: (item: T) => JSX.Element;
  renderLargeTile?: (item: T) => JSX.Element;
  renderRow?: (item: T) => JSX.Element;
  renderPill?: (item: T) => JSX.Element;
  hasNextPage?: boolean;
  isFetchingNextPage?: boolean;
  onLoadMore?: () => void;
}

type DisplayVariant = "pill" | "large-tile" | "tile" | "row";

const defaultCount = 6;
const loadingItems = Array.from(Array(defaultCount).keys());

export function DisplayGrid<T>({
  loading,
  items,
  total,
  sortOptions,
  serverSortOptions,
  serverSort,
  onServerSortChange,
  renderTile,
  renderLargeTile,
  renderRow,
  renderPill,
  getKey,
  hasNextPage,
  isFetchingNextPage,
  onLoadMore,
}: DisplayGridProps<T>) {
  const ref = useRef<HTMLDivElement>(null);
  const [variant, setVariant] = useState<DisplayVariant>(
    renderRow
      ? "row"
      : renderTile
      ? "tile"
      : renderPill
      ? "pill"
      : renderLargeTile
      ? "large-tile"
      : "tile"
  );

  const isServerPaginated = !!onLoadMore;

  const [count, setCount] = useState(defaultCount);
  const [sort, setSort] = useState<string | null>(
    sortOptions && Object.keys(sortOptions).length > 0
      ? Object.keys(sortOptions)[0]
      : null
  );

  const handleMore = () => {
    if (isServerPaginated) {
      onLoadMore?.();
    } else {
      setCount((count) => count * 2);
    }
  };

  const onLess = () => {
    setCount(defaultCount);
    ref.current?.scrollIntoView({ behavior: "smooth" });
  };

  const displayOptions: SegmentedControlItem[] = [];
  if (renderRow) displayOptions.push({ label: <IconList />, value: "row" });
  if (renderPill) displayOptions.push({ label: <IconPill />, value: "pill" });
  if (renderTile)
    displayOptions.push({ label: <IconGridDots />, value: "tile" });
  if (renderLargeTile)
    displayOptions.push({
      label: <IconLayoutGridFilled />,
      value: "large-tile",
    });

  const comparator = !isServerPaginated && sortOptions && sort ? sortOptions[sort] : null;
  const sortedItems = comparator && items ? items.sort(comparator) : items;
  const displayItems = isServerPaginated ? sortedItems : sortedItems?.slice(0, count);

  const activeSortOptions = isServerPaginated ? serverSortOptions : (sortOptions ? Object.keys(sortOptions) : undefined);
  const activeSort = isServerPaginated ? (serverSort ?? null) : sort;
  const handleSortChange = (s: string | null) => {
    if (isServerPaginated) {
      if (s) onServerSortChange?.(s);
    } else {
      setSort(s);
      setCount(defaultCount);
    }
  };

  const totalItems = total ?? items?.length ?? 0;
  const showMore = isServerPaginated
    ? (hasNextPage ?? false)
    : count < totalItems;
  const showLess = isServerPaginated ? false : count > defaultCount;

  if (!loading && displayItems?.length === 0)
    return (
      <div className={styles.noData}>
        <Text fs="italic">No data</Text>
      </div>
    );

  return (
    <>
      <div ref={ref} className={styles.controls}>
        {displayOptions.length > 1 ? (
          <SegmentedControl
            onChange={(v) => setVariant(v as DisplayVariant)}
            value={variant}
            data={displayOptions}
          />
        ) : (
          <div />
        )}

        {activeSortOptions && activeSortOptions.length > 0 && (
          <div className={styles.sortSelect}>
            <Select
              data={activeSortOptions}
              value={activeSort}
              onChange={handleSortChange}
              checkIconPosition="right"
              radius="xl"
            />
          </div>
        )}
      </div>

      <div
        className={clsx(
          styles.itemsContainer,
          variant === "row" ? styles.itemsContainerRow : styles.itemsContainerGrid
        )}
      >
        {displayItems
          ? displayItems.map((item) => (
              <div key={getKey(item)}>
                {variant === "row" && renderRow?.(item)}
                {variant === "large-tile" && renderLargeTile?.(item)}
                {variant === "tile" && renderTile?.(item)}
                {variant === "pill" && renderPill?.(item)}
              </div>
            ))
          : loadingItems.map((i) => (
              <div key={i}>
                {variant === "row" && <RowSkeleton />}
                {variant === "large-tile" && <LargeTileSkeleton />}
                {variant === "tile" && <TileSkeleton />}
                {variant === "pill" && <PillSkeleton />}
              </div>
            ))}
        {isFetchingNextPage &&
          loadingItems.map((i) => (
            <div key={`loading-${i}`}>
              {variant === "row" && <RowSkeleton />}
              {variant === "large-tile" && <LargeTileSkeleton />}
              {variant === "tile" && <TileSkeleton />}
              {variant === "pill" && <PillSkeleton />}
            </div>
          ))}
      </div>
      <div className={styles.buttons}>
        {showLess ? (
          <Button variant="light" onClick={onLess} className={styles.button}>
            <IconMinus />
          </Button>
        ) : null}
        {showMore ? (
          <Button variant="light" onClick={handleMore} className={styles.button}>
            <IconPlus />
          </Button>
        ) : null}
      </div>
    </>
  );
}
