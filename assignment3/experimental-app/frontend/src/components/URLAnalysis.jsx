import {
  ChevronDown,
  CornerDownRight,
  Info,
  MapPin,
  ShieldAlert,
} from "lucide-react";

const partNames = {
  protocol: "Connection type",
  userinfo: "Text before @",
  host: "Actual host",
  port: "Connection port",
  path: "Page path",
  query: "Extra parameters",
  fragment: "Page reference",
};
const priority = { high: 0, medium: 1, low: 2 };
const attention = {
  high: "Look closely",
  medium: "Worth checking",
  low: "Context",
};

function partExplanation(part, result) {
  switch (part.kind) {
    case "protocol":
      return result.components.scheme === "https"
        ? "HTTPS requests an encrypted connection. It does not prove that the site is genuine; no connection or certificate has been checked."
        : "HTTP does not request HTTPS encryption. Avoid sending passwords or payment information through an HTTP link.";
    case "userinfo":
      return "Everything before the final @ is sign-in information, not the website you are visiting. A familiar brand here does not identify the destination.";
    case "host":
      return `The server named by this link is ${result.components.host}. Compare the whole hostname with an address you already trust.`;
    case "port":
      return "This selects a connection port on the host. Custom ports can be legitimate, but should match the service you intended to use.";
    case "path":
      return "This names a page or resource on the host. A brand name or the word login here does not make the host official.";
    case "query":
      return `${result.components.query_parameter_count} parsed parameter(s) can pass search, tracking or other values to the site. A website address inside these values is not the current host; the site could use it to redirect, which this tool does not follow.`;
    case "fragment":
      return "Text after # is normally a page reference handled by the browser or page scripts. It is not the hostname and may change what a web app shows.";
    default:
      return "The exact submitted URL, displayed as text only.";
  }
}

export function URLBreakdown({ result, url }) {
  const supplied = result.url_parts || [];
  const parts =
    supplied.map((part) => part.text).join("") === url ? supplied : [];
  const hasUserinfo = parts.some((part) => part.kind === "userinfo");
  return (
    <div className="url-breakdown">
      <div className="analysed-url">
        <span className="eyebrow">THE ADDRESS YOU CHECKED</span>
        <code className="url-text structured-url">
          {parts.length
            ? parts.map((part, index) => (
                <span key={index} className={`url-part url-part-${part.kind}`}>
                  {part.text}
                </span>
              ))
            : url}
        </code>
        <p className="address-key">
          Purple marks the actual host.
          {hasUserinfo && " Amber marks text before @, which is not the host."}{" "}
          The address is text only.
        </p>
      </div>
      <div className="destination-box">
        <MapPin size={21} aria-hidden="true" />
        <div>
          <span className="eyebrow">THIS LINK POINTS TO</span>
          <strong>{result.components.host}</strong>
          <p>
            {hasUserinfo
              ? "Read the hostname after the final @. The familiar-looking text before it does not determine the destination."
              : "Compare this complete hostname with a trusted address before you decide to continue."}
          </p>
        </div>
      </div>
      <div className="address-context">
        <span>
          Base domain <strong>{result.components.registrable_domain}</strong>
        </span>
        <span>
          Connection{" "}
          <strong>{result.components.scheme.toUpperCase()} requested</strong>
        </span>
      </div>
      <p className="small-note">
        The base domain is a grouping from a bundled suffix list, not a verified
        owner. Shared hosting can contain different accounts under the same base
        domain.
      </p>
      {parts.length > 0 && (
        <details className="parts-disclosure">
          <summary>
            Understand the parts of this URL{" "}
            <ChevronDown size={17} aria-hidden="true" />
          </summary>
          <dl className="parts-list">
            {parts.map((part, index) => (
              <div
                key={index}
                className={part.kind === "userinfo" ? "part-caution" : ""}
              >
                <dt>{partNames[part.kind]}</dt>
                <dd>
                  <code>{part.text}</code>
                  <p>{partExplanation(part, result)}</p>
                </dd>
              </div>
            ))}
          </dl>
        </details>
      )}
    </div>
  );
}

function Observation({ signal }) {
  return (
    <article className={`observation observation-${signal.severity}`}>
      <div className="observation-heading">
        <h3>{signal.title}</h3>
        <span className="attention-badge">
          <span className={`signal-dot ${signal.severity}`} />
          {attention[signal.severity]}
        </span>
      </div>
      {signal.evidence?.length > 0 && (
        <dl className="evidence-list">
          {signal.evidence.map((item, index) => (
            <div key={index}>
              <dt>{item.label}</dt>
              <dd>
                <code>{item.value}</code>
              </dd>
            </div>
          ))}
        </dl>
      )}
      <div className="observation-copy">
        <div>
          <span className="copy-label">What this means</span>
          <p>{signal.detail}</p>
        </div>
        {signal.action && (
          <div className="observation-action">
            <span className="copy-label">
              <CornerDownRight size={14} aria-hidden="true" /> Your next step
            </span>
            <p>{signal.action}</p>
          </div>
        )}
      </div>
    </article>
  );
}

export function Findings({ result }) {
  const signals = result.signals
    .filter((s) => s.present)
    .sort((a, b) => priority[a.severity] - priority[b.severity]);
  const dangerous = result.predicted_class === 1;
  return (
    <section className="card findings-card" aria-labelledby="findings-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">READ THE SIGNS</span>
          <h2 id="findings-title">
            {signals.length
              ? `${signals.length} ${signals.length === 1 ? "thing" : "things"} to review in this URL`
              : "No listed warning patterns found"}
          </h2>
        </div>
        <ShieldAlert size={22} aria-hidden="true" />
      </div>
      <p className="findings-intro">
        {signals.length
          ? dangerous
            ? "Start with the observations below. Each one shows what we found, what it means and a practical next step."
            : "The model leans legitimate, but these visible patterns still deserve a closer look before you continue."
          : dangerous
            ? "The model flagged this URL, but these pattern checks did not find a listed warning. The model uses character patterns and 36 URL measurements; these checks cannot explain its decision on their own."
            : "These checks did not find a listed warning. That is useful context, but a dangerous website can still have an ordinary-looking URL."}
      </p>
      <div className="observation-list">
        {signals.slice(0, 3).map((signal) => (
          <Observation signal={signal} key={signal.id} />
        ))}
      </div>
      {signals.length > 3 && (
        <details className="more-observations">
          <summary>
            Show {signals.length - 3} more{" "}
            {signals.length - 3 === 1 ? "observation" : "observations"}
            <ChevronDown size={17} aria-hidden="true" />
          </summary>
          <div className="observation-list">
            {signals.slice(3).map((signal) => (
              <Observation signal={signal} key={signal.id} />
            ))}
          </div>
        </details>
      )}
      <p className="findings-limit">
        <Info size={15} aria-hidden="true" /> These are URL pattern checks, not
        the reasons behind the model's prediction. A warning pattern is not
        proof of phishing, and no warning is not proof of safety.
      </p>
    </section>
  );
}
