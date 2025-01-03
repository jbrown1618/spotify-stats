import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  build: {
    outDir: "../app/static",
    assetsDir: "",
  },
  server: {
    proxy: {
      "/api": "http://localhost:5000/",
    },
  },
  plugins: [react()],
});
