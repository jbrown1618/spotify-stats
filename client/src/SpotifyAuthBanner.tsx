import { Alert, Code } from "@mantine/core";

import { useSpotifyAuthStatus } from "./useApi";

const statusMessages = {
  missing_cache:
    "Spotify auth is not configured. Sync jobs need a refreshed Spotify cache before they can run.",
  reauth_required:
    "Spotify authorization has expired. Run the local cache refresh script and update the deployed Spotify cache before running sync jobs.",
};

export function SpotifyAuthBanner() {
  const { data } = useSpotifyAuthStatus();

  if (!data || data.status === "ok" || data.status === "error") {
    return null;
  }

  const message = statusMessages[data.status];

  return (
    <Alert
      color="yellow"
      title="Spotify authorization needs attention"
      mt="md"
    >
      {message} Cache refresh failures from Spotify return <Code>invalid_grant</Code>.
    </Alert>
  );
}
