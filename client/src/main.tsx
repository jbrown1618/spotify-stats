import "./global.css";
import "@mantine/core/styles.css";
import "@mantine/charts/styles.css";

import { MantineProvider } from "@mantine/core";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Outlet, Route, Routes } from "react-router";

import { SummaryPage } from "./SummaryPage.tsx";
import {
  WrappedForYear,
  WrappedPage,
  WrappedTimeFramePicker,
} from "./WrappedPage.tsx";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <MantineProvider
          defaultColorScheme="dark"
          theme={{ primaryColor: "green" }}
        >
          <Routes>
            <Route path="/" element={<SummaryPage />} />
            <Route
              path="/wrapped"
              element={
                <WrappedPage>
                  <Outlet />
                </WrappedPage>
              }
            >
              <Route index element={<WrappedTimeFramePicker />} />
              <Route path=":year" element={<WrappedForYear />} />
            </Route>
          </Routes>
        </MantineProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </StrictMode>
);
