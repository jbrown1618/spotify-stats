import { Anchor } from "@mantine/core";

import SpotifyIcon from "../../spotify.svg";

export function SpotifyLink({
  uri,
  text,
}: {
  uri: string;
  text?: string | JSX.Element;
}) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_, itemType, itemID] = uri.split(":");
  const href = `https://open.spotify.com/${itemType}/${itemID}`;

  return (
    <Anchor
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      variant="muted"
      underline="hover"
      onClick={(e) => e.stopPropagation()}
    >
      <img
        src={SpotifyIcon}
        style={{ height: 14, width: 14, marginRight: 4 }}
      />
      {text ?? "Open"}
    </Anchor>
  );
}
