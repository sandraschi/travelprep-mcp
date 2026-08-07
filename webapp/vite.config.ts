import { fileURLToPath } from "url";
import { dirname, resolve } from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 11100,
    proxy: {
      "/api": { target: "http://127.0.0.1:11099", changeOrigin: true },
      "/skill": { target: "http://127.0.0.1:11099", changeOrigin: true },
      "/docs": { target: "http://127.0.0.1:11099", changeOrigin: true },
      "/redoc": { target: "http://127.0.0.1:11099", changeOrigin: true },
      "/openapi.json": { target: "http://127.0.0.1:11099", changeOrigin: true },
    },
  },
});
