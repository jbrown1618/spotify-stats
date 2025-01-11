import { Anchor, Container, useMantineTheme } from "@mantine/core";
import { PropsWithChildren, ReactNode } from "react";

import { useIsMobile } from "../useIsMobile";

interface LayoutProps {
  title: string;
  headerControl?: ReactNode;
}

export function Layout({
  title,
  headerControl,
  children,
}: PropsWithChildren<LayoutProps>) {
  const isMobile = useIsMobile();
  const t = useMantineTheme();

  return (
    <>
      <div
        style={{
          width: "100%",
          height: isMobile ? 40 : 170,
          backgroundColor: t.colors.green[9],
          position: "absolute",
          zIndex: -1,
        }}
      ></div>
      <Container size="lg">
        <nav
          style={{
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <h1 style={{ margin: 0, whiteSpace: "nowrap" }}>{title}</h1>
          <div>{headerControl}</div>
        </nav>

        {children}

        <footer style={{ padding: 16, textAlign: "center" }}>
          <Anchor
            href="https://www.github.com/jbrown1618/spotify-stats"
            target="_blank"
            underline="hover"
          >
            jbrown1618/spotify-stats
          </Anchor>
        </footer>
      </Container>
    </>
  );
}
