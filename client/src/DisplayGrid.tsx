import { Grid, GridCol, Skeleton } from "@mantine/core";

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
  return (
    <Grid>
      {items
        ? items.slice(0, defaultGridCount).map((item) => (
            <GridCol span={renderTile ? 2 : 12} key={getKey(item)}>
              {renderTile ? renderTile(item) : renderRow(item)}
            </GridCol>
          ))
        : loadingItems.map((_, i) => (
            <GridCol span={renderTile ? 2 : 12} key={i}>
              <Skeleton width="100%" height={200} />
            </GridCol>
          ))}
    </Grid>
  );
}
