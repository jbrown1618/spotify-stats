import { Skeleton } from "@mantine/core";

import { TextSkeleton } from "./TextSkeleton";

export function ChartSkeleton() {
  return (
    <>
      <TextSkeleton style="h3" />
      <Skeleton w="100%" h="60vh" />
    </>
  );
}
