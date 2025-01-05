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
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      style={{ color: "white" }}
      onClick={(e) => e.stopPropagation()}
    >
      {text ?? "Open"}
    </a>
  );
}
