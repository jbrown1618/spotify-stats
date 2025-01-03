import "@mantine/core/styles.css";
import "@mantine/charts/styles.css";

import { MantineProvider } from "@mantine/core";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App.tsx";
import { FiltersProvider } from "./FiltersProvider.tsx";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <FiltersProvider>
      <QueryClientProvider client={queryClient}>
        <MantineProvider
          defaultColorScheme="dark"
          theme={{ primaryColor: "green" }}
        >
          <App />
        </MantineProvider>
      </QueryClientProvider>
    </FiltersProvider>
  </StrictMode>
);
