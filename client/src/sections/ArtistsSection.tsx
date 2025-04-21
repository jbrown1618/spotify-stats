import { Tabs } from "@mantine/core";

import { ArtistsBarChart } from "../charts/ArtistsBarChart";
import { ArtistStreamsLineChart } from "../charts/ArtistsLineChart";
import { ArtistsStreamingHistoryStack } from "../charts/ArtistsStreamingHistoryStack";
import { DisplayGrid } from "../design/DisplayGrid";
import { ArtistRow } from "../list-items/ArtistRow";
import { ArtistTile } from "../list-items/ArtistTile";
import { artistSortOptions } from "../sorting";
import { useArtists } from "../useApi";
import { useFilters } from "../useFilters";

export function ArtistsSection() {
  const filters = useFilters();

  if (filters.artists?.length === 1) return null;

  return (
    <div>
      <h2>Artists</h2>

      <Tabs defaultValue="months">
        <Tabs.List>
          <Tabs.Tab value="months">Months</Tabs.Tab>
          <Tabs.Tab value="streams">Streams</Tabs.Tab>
          <Tabs.Tab value="count">Count</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="streams">
          <ArtistStreamsLineChart />
        </Tabs.Panel>

        <Tabs.Panel value="count">
          <ArtistsBarChart />
        </Tabs.Panel>

        <Tabs.Panel value="months">
          <ArtistsStreamingHistoryStack />
        </Tabs.Panel>
      </Tabs>

      <ArtistsDisplayGrid />
    </div>
  );
}

function ArtistsDisplayGrid() {
  const { data: artists } = useArtists();
  return (
    <DisplayGrid
      items={artists ? Object.values(artists) : undefined}
      sortOptions={artistSortOptions}
      getKey={(artist) => artist.artist_uri}
      renderTile={(artist) => <ArtistTile artist={artist} />}
      renderLargeTile={(artist) => <ArtistTile large artist={artist} />}
      renderRow={(artist) => <ArtistRow artist={artist} />}
    />
  );
}
