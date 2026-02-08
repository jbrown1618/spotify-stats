import "@mantine/core/styles.css";
import "@mantine/charts/styles.css";

import { MantineProvider, MantineThemeOverride } from "@mantine/core";
import { createAsyncStoragePersister } from "@tanstack/query-async-storage-persister";
import { QueryClient } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App.tsx";
import { FiltersProvider } from "./FiltersProvider.tsx";

const queryClient = new QueryClient();

const persister = createAsyncStoragePersister({
  storage: window.localStorage,
});

const maxPersistAge = 2 * 24 * 60 * 60 * 1000; // 2 days

const theme: MantineThemeOverride = {
  primaryColor: "green",
};

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <FiltersProvider>
      <PersistQueryClientProvider
        client={queryClient}
        persistOptions={{
          persister,
          maxAge: maxPersistAge,
          buster: import.meta.env.VITE_BUILD_ID ?? "dev",
        }}
      >
        <MantineProvider defaultColorScheme="dark" theme={theme}>
          <App />
          <ReactQueryDevtools initialIsOpen={false} />
        </MantineProvider>
      </PersistQueryClientProvider>
    </FiltersProvider>
  </StrictMode>,
);
