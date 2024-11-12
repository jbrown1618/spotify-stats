import { Grid, GridCol, Skeleton } from "@mantine/core";

interface DisplayGridProps<T> {
  items: T[] | undefined;
  loading: boolean;
  getKey: (item: T) => string;
  renderTile?: (item: T) => JSX.Element;
  renderRow: (item: T) => JSX.Element;
}

const defaultGridCount = 1 * 2 * 3 * 5;
const loadingItems = new Array(defaultGridCount).map(() => null);

export function DisplayGrid<T>({
  items,
  loading,
  renderTile,
  renderRow,
  getKey,
}: DisplayGridProps<T>) {
  return (
    <Grid>
      {items && !loading
        ? items.slice(0, defaultGridCount).map((item) => (
            <GridCol span={renderTile ? 2 : 12} key={getKey(item)}>
              {renderTile ? renderTile(item) : renderRow(item)}
            </GridCol>
          ))
        : loadingItems.map(() => <Skeleton width="100%" height={200} />)}
    </Grid>
  );
}
