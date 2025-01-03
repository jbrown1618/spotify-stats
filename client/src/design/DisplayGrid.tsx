import { Button, SegmentedControl, SegmentedControlItem } from "@mantine/core";
import {
  IconGridDots,
  IconLayoutGridFilled,
  IconList,
  IconPill,
} from "@tabler/icons-react";
import { useState } from "react";

import { LargeTileSkeleton } from "./LargeTileDesign";
import { PillSkeleton } from "./PillDesign";
import { RowSkeleton } from "./RowDesign";
import { TileSkeleton } from "./TileDesign";

interface DisplayGridProps<T> {
  items: T[] | undefined;
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
  items,
  renderTile,
  renderLargeTile,
  renderRow,
  renderPill,
  getKey,
}: DisplayGridProps<T>) {
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

  const onMore = () => setCount((count) => count * 2);

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

  return (
    <>
      {displayOptions.length > 1 && (
        <SegmentedControl
          onChange={(v) => setVariant(v as DisplayVariant)}
          value={variant}
          data={displayOptions}
        />
      )}
      <div
        style={{
          marginTop: 16,
          display: "flex",
          flexDirection: variant === "row" ? "column" : "row",
          flexWrap: variant === "row" ? undefined : "wrap",
          gap: 16,
          justifyContent: variant === "row" ? "left" : "center",
        }}
      >
        {items
          ? items.slice(0, count).map((item) => (
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
      {count < (items?.length ?? 0) ? (
        <Button variant="light" onClick={onMore} style={{ marginTop: 16 }}>
          More
        </Button>
      ) : null}
    </>
  );
}
