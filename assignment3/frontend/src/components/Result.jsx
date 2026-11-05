import {
  AlertTriangle,
  ArrowRight,
  Check,
  CornerDownRight,
  Info,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { SignalChart } from "./Charts.jsx";
import { Findings, URLBreakdown } from "./URLAnalysis.jsx";

export default function Result({ result, url, onInsights }) {
  const dangerous = result.predicted_class === 1;
  const Icon = dangerous ? ShieldAlert : ShieldCheck;
  const present = result.signals.filter((signal) => signal.present);
  return (
    <div className="result-area">
      <section
        className={`card result-card ${dangerous ? "dangerous" : "benign"}`}
        aria-labelledby="result-title"
      >
        <div className="result-overline">
          <span className="eyebrow">YOUR ANALYSIS</span>
          <span className="status-pill">
            <Check size={13} /> Complete
          </span>
        </div>
        <div className="result-main">
          <span className="result-icon">
            <Icon size={34} aria-hidden="true" />
          </span>
          <div>
            <h2 id="result-title">{result.label}</h2>
            <p>{result.explanation}</p>
          </div>
        </div>
        <div className="confidence-block">
          <div>
            <span>Model confidence in this label</span>
            <strong>
              {(result.confidence * 100).toFixed(1)}
              <small>%</small>
            </strong>
          </div>
          <div
            className="confidence-track"
            role="meter"
            aria-label="Predicted-class model confidence"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(result.confidence * 100)}
          >
            <span style={{ width: `${result.confidence * 100}%` }} />
          </div>
          <p>
            Uncalibrated model estimate · not a measured probability of
            real-world harm
          </p>
        </div>
        {result.uncertain && (
          <div className="uncertain">
            <AlertTriangle size={17} />
            <span>
              Close to the decision boundary. Treat this result with extra
              caution.
            </span>
          </div>
        )}
        <URLBreakdown result={result} url={url} />
        <div className="result-foot">
          <span>
            <Info size={15} />
            {result.disclaimer}
          </span>
          <span>{Math.round(result.analysis_ms)} ms · 36 features</span>
        </div>
      </section>
      <Findings result={result} />
      <div className="result-grid">
        <SignalChart result={result} />
        <section className="card guidance-card">
          <span className="eyebrow">YOUR NEXT MOVE</span>
          <h2>A little caution goes a long way.</h2>
          <p className="muted">
            Use this analysis as one clue, together with the context in which
            you received the link.
          </p>
          <ol className="guidance-list">
            <li>
              <span>01</span>
              <div>
                <strong>Check the real domain.</strong>
                <p>
                  Trusted words elsewhere in a URL do not establish who owns the
                  destination.
                </p>
              </div>
            </li>
            <li>
              <span>02</span>
              <div>
                <strong>Go directly when in doubt.</strong>
                <p>
                  Use a known bookmark or type the organisation’s address
                  yourself.
                </p>
              </div>
            </li>
            <li>
              <span>03</span>
              <div>
                <strong>Protect your information.</strong>
                <p>
                  Avoid entering passwords, payment details or recovery codes
                  into an unverified site.
                </p>
              </div>
            </li>
          </ol>
          <button className="text-button" onClick={onInsights}>
            Explore session insights <ArrowRight size={16} />
          </button>
          <div className="signal-count">
            <CornerDownRight size={18} />
            <span>
              <strong>{present.length}</strong> observed signals. Their presence
              or absence does not establish safety.
            </span>
          </div>
        </section>
      </div>
    </div>
  );
}
