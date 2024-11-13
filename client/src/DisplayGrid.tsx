import { Grid, GridCol, SegmentedControl, Skeleton } from "@mantine/core";
import {
  IconGridDots,
  IconLayoutGridFilled,
  IconList,
} from "@tabler/icons-react";
import { useState } from "react";

interface DisplayGridProps<T> {
  items: T[] | undefined;
  getKey: (item: T) => string;
  renderTile?: (item: T) => JSX.Element;
  renderRow: (item: T) => JSX.Element;
}

const defaultGridCount = 1 * 2 * 3 * 5;
const loadingItems = new Array(defaultGridCount).map((_, i) => i);

export function DisplayGrid<T>({
  items,
  renderTile,
  renderRow,
  getKey,
}: DisplayGridProps<T>) {
  const [span, setSpan] = useState(renderTile ? 2 : 12);
  return (
    <>
      {renderTile && (
        <SegmentedControl
          onChange={(v) => setSpan(parseInt(v))}
          value={span + ""}
          data={[
            { label: <IconList />, value: "12" },
            { label: <IconGridDots />, value: "2" },
            { label: <IconLayoutGridFilled />, value: "4" },
          ]}
        />
      )}
      <Grid>
        {items
          ? items.slice(0, defaultGridCount).map((item) => (
              <GridCol span={span} key={getKey(item)}>
                {renderTile && span !== 12 ? renderTile(item) : renderRow(item)}
              </GridCol>
            ))
          : loadingItems.map((_, i) => (
              <GridCol span={span} key={i}>
                <Skeleton width="100%" height={200} />
              </GridCol>
            ))}
      </Grid>
    </>
  );
}
