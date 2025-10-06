import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src")
    }
  },
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://localhost:5000",
      "/bets": "http://localhost:5000",
      "/stats": "http://localhost:5000",
      "/admin": "http://localhost:5000",
      "/files": "http://localhost:5000"
    }
  },
  build: { outDir: "dist", emptyOutDir: true },
  base: "/static/admin/"
});