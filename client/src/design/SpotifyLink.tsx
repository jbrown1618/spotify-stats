import { Anchor } from "@mantine/core";

import SpotifyIcon from "../../spotify.svg";

export function SpotifyLink({
  uri,
  text,
  size,
}: {
  uri: string;
  text?: string | JSX.Element;
  size?: number;
}) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_, itemType, itemID] = uri.split(":");
  const href = `https://open.spotify.com/${itemType}/${itemID}`;
  size ??= 14;

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
        style={{ height: size, width: size, marginRight: 4 }}
      />
      {text}
    </Anchor>
  );
}
