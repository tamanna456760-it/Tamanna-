import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // The production site uses the custom domain www.bd-king-r7.com at the domain root.
  // Keep generated asset URLs rooted at "/" rather than a repository sub-path.
  base: "/",
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": "http://localhost:3001",
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
