import {
  Button,
  Grid,
  GridCol,
  SegmentedControl,
  SegmentedControlItem,
  Skeleton,
} from "@mantine/core";
import {
  IconGridDots,
  IconLayoutGridFilled,
  IconList,
  IconPill,
} from "@tabler/icons-react";
import { useState } from "react";

interface DisplayGridProps<T> {
  items: T[] | undefined;
  getKey: (item: T) => string;
  renderTile?: (item: T) => JSX.Element;
  renderLargeTile?: (item: T) => JSX.Element;
  renderRow?: (item: T) => JSX.Element;
  renderPill?: (item: T) => JSX.Element;
}

type DisplayVariant = "pill" | "large-tile" | "tile" | "row";

const defaultGridCount = 12;
const defaultRowCount = 10;
const loadingItems = Array.from(Array(defaultGridCount).keys());

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

  const [count, setCount] = useState(
    variant === "row" ? defaultRowCount : defaultGridCount
  );

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
      <Grid>
        {items
          ? items.slice(0, count).map((item) => (
              <GridCol span={spanByVariant[variant]} key={getKey(item)}>
                {variant === "row" && renderRow?.(item)}
                {variant === "large-tile" && renderLargeTile?.(item)}
                {variant === "tile" && renderTile?.(item)}
                {variant === "pill" && renderPill?.(item)}
              </GridCol>
            ))
          : loadingItems.map((i) => (
              <GridCol span={spanByVariant[variant]} key={i}>
                <Skeleton width="100%" height={loadingItemHeights[variant]} />
              </GridCol>
            ))}
      </Grid>
      {count < (items?.length ?? 0) ? (
        <Button variant="light" onClick={onMore} style={{ marginTop: 16 }}>
          More
        </Button>
      ) : null}
    </>
  );
}

const spanByVariant: Record<DisplayVariant, number> = {
  "large-tile": 4,
  tile: 2,
  pill: 3,
  row: 12,
};

const loadingItemHeights: Record<DisplayVariant, string | number> = {
  row: 70,
  "large-tile": "20vw",
  pill: 28,
  tile: "15vw",
};
