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
import { useRef, useState } from "react";

import { SortOptions } from "../sorting";
import { LargeTileSkeleton } from "./LargeTileDesign";
import { PillSkeleton } from "./PillDesign";
import { RowSkeleton } from "./RowDesign";
import { TileSkeleton } from "./TileDesign";

interface DisplayGridProps<T> {
  loading: boolean;
  items: T[] | undefined;
  sortOptions?: SortOptions<T>;
  getKey: (item: T) => string;
  renderTile?: (item: T) => JSX.Element;
  renderLargeTile?: (item: T) => JSX.Element;
  renderRow?: (item: T) => JSX.Element;
  renderPill?: (item: T) => JSX.Element;
}

type DisplayVariant = "pill" | "large-tile" | "tile" | "row";

const defaultCount = 6;
const loadingItems = Array.from(Array(defaultCount).keys());

export function DisplayGrid<T>({
  loading,
  items,
  sortOptions,
  renderTile,
  renderLargeTile,
  renderRow,
  renderPill,
  getKey,
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

  const [count, setCount] = useState(defaultCount);
  const [sort, setSort] = useState<string | null>(
    sortOptions && Object.keys(sortOptions).length > 0
      ? Object.keys(sortOptions)[0]
      : null
  );

  const onMore = () => setCount((count) => count * 2);
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

  const comparator = sortOptions && sort ? sortOptions[sort] : null;
  const displayItems = comparator && items ? items.sort(comparator) : items;

  if (!loading && displayItems?.length === 0)
    return (
      <div style={{ display: "flex", justifyContent: "center" }}>
        <Text fs="italic">No data</Text>
      </div>
    );

  return (
    <>
      <div
        ref={ref}
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 16,
          marginTop: 8,
          alignItems: "center",
        }}
      >
        {displayOptions.length > 1 ? (
          <SegmentedControl
            onChange={(v) => setVariant(v as DisplayVariant)}
            value={variant}
            data={displayOptions}
          />
        ) : (
          <div />
        )}

        {sortOptions && Object.keys(sortOptions).length > 0 && (
          <div style={{ maxWidth: 150 }}>
            <Select
              data={Object.keys(sortOptions)}
              value={sort}
              onChange={(s) => {
                setSort(s);
                setCount(defaultCount);
              }}
              checkIconPosition="right"
              radius="xl"
            />
          </div>
        )}
      </div>

      <div
        style={{
          marginTop: 8,
          display: "flex",
          flexDirection: variant === "row" ? "column" : "row",
          flexWrap: variant === "row" ? undefined : "wrap",
          gap: 16,
          justifyContent: variant === "row" ? "left" : "center",
        }}
      >
        {displayItems
          ? displayItems.slice(0, count).map((item) => (
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
      </div>
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        {count > defaultCount ? (
          <Button variant="light" onClick={onLess} style={{ marginTop: 16 }}>
            <IconMinus />
          </Button>
        ) : null}
        {count < (items?.length ?? 0) ? (
          <Button variant="light" onClick={onMore} style={{ marginTop: 16 }}>
            <IconPlus />
          </Button>
        ) : null}
      </div>
    </>
  );
}
