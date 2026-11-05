import {
  ArrowRight,
  BarChart3,
  CheckCheck,
  RotateCcw,
  ShieldAlert,
} from "lucide-react";
import { SessionChart, SignalChart } from "../components/Charts.jsx";

export default function InsightsPage({
  history,
  result,
  loading,
  onClear,
  onCheck,
}) {
  const dangerous = history.filter(
    (entry) => entry.predictedClass === 1,
  ).length;
  return (
    <>
      <div className="page-heading compact">
        <div>
          <span className="eyebrow">THE BIGGER PICTURE</span>
          <h1>
            A clearer view
            <br />
            <span>of this session.</span>
          </h1>
          <p>
            Explore anonymous model scores and the signals behind your latest
            check.
          </p>
        </div>
        <button
          className="button secondary"
          disabled={!history.length || loading}
          onClick={onClear}
        >
          <RotateCcw size={16} /> Clear session
        </button>
      </div>
      <div className="stat-grid">
        <div className="card stat">
          <BarChart3 size={20} />
          <span>Checks in memory</span>
          <strong>
            {history.length}
            <small>/ 20</small>
          </strong>
        </div>
        <div className="card stat">
          <ShieldAlert size={20} />
          <span>Potentially dangerous</span>
          <strong>{dangerous}</strong>
        </div>
        <div className="card stat">
          <CheckCheck size={20} />
          <span>Likely legitimate</span>
          <strong>{history.length - dangerous}</strong>
        </div>
      </div>
      <div className="insights-grid">
        <SessionChart history={history} />
        {result ? (
          <SignalChart result={result} />
        ) : (
          <section className="card insights-empty">
            <div className="feature-icon mint">
              <BarChart3 size={30} />
            </div>
            <h2>Every check adds context.</h2>
            <p>
              Analyse a URL to explore the observed signals in your current
              result.
            </p>
            <button className="button primary" onClick={onCheck}>
              Check your first URL <ArrowRight size={17} />
            </button>
          </section>
        )}
      </div>
      <section className="card insight-notice">
        <h2>What these charts can tell you</h2>
        <p>
          The model score estimates membership in the combined dangerous class.
          Signal counts describe URL patterns and do not measure how much a
          feature influenced the prediction. Neither chart measures website
          safety.
        </p>
        <p>
          Only the most recent 20 anonymous scores are kept in memory.
          Refreshing or clearing the session removes them. No URLs, hosts or
          query strings are stored in this comparison.
        </p>
      </section>
    </>
  );
}
