import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Findings, URLBreakdown } from "../src/components/URLAnalysis.jsx";

const result = {
  predicted_class: 1,
  components: {
    scheme: "https",
    host: "account-check.example",
    registrable_domain: "account-check.example",
    query_parameter_count: 0,
  },
  url_parts: [
    { kind: "protocol", text: "https://" },
    { kind: "userinfo", text: "paypal.com@" },
    { kind: "host", text: "account-check.example" },
    { kind: "path", text: "/login" },
  ],
  signals: [],
};
const render = (component, props) =>
  renderToStaticMarkup(createElement(component, props));

describe("readable URL analysis", () => {
  it("shows the real host and explains userinfo instead of treating the brand as the destination", () => {
    const html = render(URLBreakdown, {
      result,
      url: "https://paypal.com@account-check.example/login",
    });
    expect(html).toContain("url-part-userinfo");
    expect(html).toContain("THIS LINK POINTS TO");
    expect(html).toContain("account-check.example");
    expect(html).toContain("Everything before the final @");
    expect(html).not.toContain("<a ");
  });
  it("keeps hostile URL and evidence strings as escaped text", () => {
    const payload = "<img src=x onerror=alert(1)>";
    const unsafe = {
      ...result,
      components: { ...result.components, host: payload },
      url_parts: [{ kind: "host", text: payload }],
    };
    const html = render(URLBreakdown, { result: unsafe, url: payload });
    expect(html).toContain("&lt;img");
    expect(html).not.toContain("<img");
    expect(html).not.toContain("<script");
    const evidence = render(Findings, {
      result: {
        ...result,
        signals: [
          {
            id: "x",
            title: "Example",
            severity: "high",
            present: true,
            detail: payload,
            action: payload,
            evidence: [{ label: "URL text", value: payload }],
          },
        ],
      },
    });
    expect(evidence).not.toContain("<img");
    expect(evidence).toContain("&lt;img");
  });
  it("does not invent model explanations when its dangerous result has no visible warning", () => {
    const html = render(Findings, { result });
    expect(html).toContain("The model flagged this URL");
    expect(html).toContain("these checks cannot explain its decision");
    expect(html).not.toContain("observation-heading");
  });
  it("still shows warning patterns for a benign model prediction and collapses extra observations", () => {
    const signals = ["low", "high", "medium", "low"].map((severity, i) => ({
      id: String(i),
      title: `Finding ${i}`,
      severity,
      present: true,
      detail: "Context",
      action: "Check host",
      evidence: [],
    }));
    const html = render(Findings, {
      result: { ...result, predicted_class: 0, signals },
    });
    expect(html).toContain("The model leans legitimate");
    expect(html.indexOf("Finding 1")).toBeLessThan(html.indexOf("Finding 0"));
    expect(html).toContain("Show 1 more observation");
    expect(html).toContain("<details");
  });
});
