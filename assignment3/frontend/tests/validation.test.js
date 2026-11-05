import { describe, expect, it } from "vitest";
import { sessionEntry, validateURL } from "../src/validation.js";

describe("URL input validation", () => {
  it.each([
    "",
    "example.com/",
    "javascript:alert(1)",
    "https://",
    "https://example.com:99999/",
    "https://example.com/has space",
    "https://example.com/%zz",
    "https://example.com/" + "a".repeat(2048),
  ])("rejects %s", (url) => expect(validateURL(url)).not.toBe(""));
  it.each([
    "https://example.com/",
    "HTTP://example.com/path",
    "https://paypal.com@account.example/login",
    "https://[::1]/",
  ])("accepts complete input %s", (url) => expect(validateURL(url)).toBe(""));
});
it("keeps URLs and hosts out of session history", () => {
  const entry = sessionEntry(
    {
      label: "Likely legitimate",
      predicted_class: 0,
      dangerous_probability: 0.1,
      confidence: 0.9,
      url: "secret",
      url_parts: [{ kind: "query", text: "?token=secret" }],
      components: { host: "secret.example" },
      signals: [
        {
          present: true,
          evidence: [{ label: "Query", value: "secret" }],
          action: "secret",
        },
      ],
    },
    1,
  );
  expect(entry.score).toBe(10);
  expect(entry.confidence).toBe(90);
  expect(entry.signals).toBe(1);
  expect(JSON.stringify(entry)).not.toContain("secret");
});
