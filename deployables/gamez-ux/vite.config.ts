import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";

/**
 * Where the gateway answers while developing on this machine.
 *
 * The browser calls a path under GATEWAY_PREFIX, and the dev server forwards
 * it. In a container nginx does the same thing, so the application never sees
 * a cross-origin request and never needs one allowed.
 */
const LOCAL_GATEWAY_ORIGIN = "http://127.0.0.1:8080";
const GATEWAY_PREFIX = "/api";
const DEV_SERVER_PORT = 5173;

function repositoryPath(relative: string): string {
  return fileURLToPath(new URL(`../../${relative}`, import.meta.url));
}

/**
 * The ux package is compiled from source. Its modules are a mix of .ts and
 * .tsx, and one export pattern cannot name both extensions, so it is mapped
 * here and in tsconfig.json rather than resolved as a package.
 */
const UX_SOURCE_ALIAS = {
  find: /^@board-gamez\/ux\/(.*)$/,
  replacement: repositoryPath("packages/ux/src_tsx/$1"),
};

export default defineConfig({
  plugins: [react()],
  resolve: { alias: [UX_SOURCE_ALIAS] },
  // The settings document is served beside the bundle, so a container can be
  // pointed at another gateway by mounting a different file over it.
  publicDir: fileURLToPath(new URL("./config", import.meta.url)),
  server: {
    port: DEV_SERVER_PORT,
    strictPort: true,
    fs: { allow: [repositoryPath(".")] },
    proxy: {
      [GATEWAY_PREFIX]: {
        target: LOCAL_GATEWAY_ORIGIN,
        changeOrigin: true,
        rewrite: (path: string) => path.replace(GATEWAY_PREFIX, ""),
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: false,
    // Split the vendor code out, so a change to this application does not make
    // a returning browser download React and MUI again.
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom", "react-dom/client"],
          mui: ["@mui/material", "@emotion/react", "@emotion/styled"],
          query: ["@tanstack/react-query"],
        },
      },
    },
  },
});
