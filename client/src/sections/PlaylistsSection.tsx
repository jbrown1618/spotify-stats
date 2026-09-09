import { PlaylistsBarChart } from "../charts/PlaylistsBarChart";
import { DisplayGrid } from "../design/DisplayGrid";
import { PlaylistRow } from "../list-items/PlaylistRow";
import { PlaylistTile } from "../list-items/PlaylistTile";
import { PAGE_SIZE, usePlaylists } from "../useApi";
import { SectionHeading } from "./SectionHeading";

export function PlaylistsSection() {
  const { items, total, isLoading, fetchNextPage, isFetchingNextPage } =
    usePlaylists({ sort: "Most liked tracks", limit: PAGE_SIZE });

  return (
    <div>
      <SectionHeading title="Playlists" total={total} />

      <PlaylistsBarChart />
      <DisplayGrid
        loading={isLoading}
        items={items}
        total={total}
        getKey={(playlist) => playlist.playlist_uri}
        renderTile={(playlist) => <PlaylistTile playlist={playlist} />}
        renderRow={(playlist) => <PlaylistRow playlist={playlist} />}
        isFetchingNextPage={isFetchingNextPage}
        onLoadMore={() => fetchNextPage()}
      />
    </div>
  );
}
