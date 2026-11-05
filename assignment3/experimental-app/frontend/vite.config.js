import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { randomBytes } from "node:crypto";

const nonce = randomBytes(18).toString("base64");

const headers = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "no-referrer",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "Content-Security-Policy": `default-src 'self'; script-src 'self' 'nonce-${nonce}'; style-src 'self' 'nonce-${nonce}'; img-src 'self' data:; connect-src 'self' http://127.0.0.1:8001 ws://127.0.0.1:5174; font-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'`,
};
export default defineConfig({
  plugins: [react()],
  html: { cspNonce: nonce },
  server: { headers, allowedHosts: ["127.0.0.1", "localhost"] },
  preview: { headers, allowedHosts: ["127.0.0.1", "localhost"] },
  test: { include: ["tests/**/*.test.js"] },
});
