import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  define: {
    "import.meta.env.VITE_BUILD_ID": JSON.stringify(new Date().toISOString()),
  },
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
