import {
  ArrowRight,
  Cpu,
  CircleHelp,
  Link2,
  LoaderCircle,
  LockKeyhole,
  Search,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { lazy, Suspense } from "react";
const Result = lazy(() => import("../components/Result.jsx"));

export default function CheckPage({
  draft,
  setDraft,
  onSubmit,
  loading,
  error,
  result,
  resultURL,
  onInsights,
  focusRef,
}) {
  return (
    <>
      <div className="page-heading check-heading">
        <div>
          <span className="hero-kicker">
            <Sparkles size={14} aria-hidden="true" /> A LITTLE INTELLIGENCE. A
            CLEARER NEXT STEP.
          </span>
          <h1>
            Understand the link.
            <br />
            <span>Before you follow it.</span>
          </h1>
          <p>
            Look beyond the address. Check a URL’s textual signals
            <br className="desktop-break" /> with a local machine learning
            model.
          </p>
        </div>
        <div className="hero-emblem" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <ShieldCheck size={42} strokeWidth={1.3} />
          <span className="emblem-dot">
            <Sparkles size={14} />
          </span>
        </div>
      </div>
      <section className="card input-card" aria-labelledby="input-title">
        <div className="section-heading">
          <div>
            <span className="eyebrow">URL INTELLIGENCE</span>
            <h2 id="input-title">What link are you looking at?</h2>
          </div>
        </div>
        <form onSubmit={onSubmit} noValidate>
          <label htmlFor="url-input">Website URL</label>
          <div className={`input-row ${error ? "has-error" : ""}`}>
            <Link2 size={20} aria-hidden="true" />
            <input
              ref={focusRef}
              id="url-input"
              name="url"
              type="text"
              inputMode="url"
              autoComplete="off"
              autoCapitalize="none"
              spellCheck={false}
              placeholder="https://example.com/a-link-to-check"
              value={draft}
              disabled={loading}
              onChange={(e) => setDraft(e.target.value)}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? "url-error url-help" : "url-help"}
            />
            {draft && !loading && (
              <button
                type="button"
                className="clear-input"
                aria-label="Clear URL"
                onClick={() => {
                  setDraft("");
                  focusRef.current?.focus();
                }}
              >
                <X size={16} />
              </button>
            )}
            <div className="composer-actions">
              <span className="model-caption">
                <Cpu size={14} aria-hidden="true" /> URL text model{" "}
                <span>· Text patterns + 36 measurements</span>
              </span>
              <button
                className="button primary"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <LoaderCircle className="spin" size={17} /> Analysing…
                  </>
                ) : (
                  <>
                    Analyse link <ArrowRight size={17} />
                  </>
                )}
              </button>
            </div>
          </div>
          {error && (
            <p className="field-error" id="url-error" role="alert">
              {error.message || error}
              {error.requestId && (
                <span> Reference: {error.requestId.slice(0, 8)}</span>
              )}
            </p>
          )}
          <div className="input-help" id="url-help">
            <span>
              Use a complete http:// or https:// URL. Maximum 2,048 characters.
            </span>
            <span>{draft.length.toLocaleString()} / 2,048</span>
          </div>
          <div className="example-row">
            <span>Try an example</span>
            <button
              type="button"
              disabled={loading}
              onClick={() => {
                setDraft("https://example.com/");
                focusRef.current?.focus();
              }}
            >
              A simple address <ArrowRight size={12} />
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => {
                setDraft("https://paypal.com@account-check.example/login");
                focusRef.current?.focus();
              }}
            >
              A misleading address <ArrowRight size={12} />
            </button>
          </div>
        </form>
        <div className="privacy-line">
          <LockKeyhole size={14} />
          <span>
            Your URL goes only to the local backend. It is not saved, opened or
            sent to a third-party service.
          </span>
        </div>
      </section>
      <div className="sr-only" role="status" aria-live="polite">
        {loading
          ? "Analysing URL. Please wait."
          : result
            ? `Analysis complete: ${result.label}.`
            : ""}
      </div>
      {loading && (
        <section className="card loading-card" aria-busy="true">
          <LoaderCircle size={27} className="spin" />
          <h2>Reading the signs in your link…</h2>
          <p>Extracting URL features. The destination is never opened.</p>
        </section>
      )}
      {!loading && result && (
        <Suspense
          fallback={
            <section className="card loading-card" role="status">
              Preparing your result…
            </section>
          }
        >
          <Result result={result} url={resultURL} onInsights={onInsights} />
        </Suspense>
      )}
      {!loading && !result && (
        <>
          <div className="section-label">
            <span>DESIGNED TO INFORM, NOT TO PROMISE</span>
            <span className="label-rule" />
          </div>
          <div className="feature-grid">
            <article className="feature-card">
              <span className="feature-icon mint">
                <Search size={23} />
              </span>
              <h3>Read the address</h3>
              <p>
                Look for unusual structure, hidden hosts and misleading tokens
                in the URL itself.
              </p>
              <span className="feature-number">01</span>
            </article>
            <article className="feature-card">
              <span className="feature-icon blue">
                <ShieldCheck size={23} />
              </span>
              <h3>See the model’s view</h3>
              <p>
                Get an experimental model prediction with its confidence and
                honest limitations.
              </p>
              <span className="feature-number">02</span>
            </article>
            <article className="feature-card">
              <span className="feature-icon sand">
                <CircleHelp size={23} />
              </span>
              <h3>Choose your next step</h3>
              <p>
                Understand the observed signals, then use context and caution
                before taking action.
              </p>
              <span className="feature-number">03</span>
            </article>
          </div>
          <div className="model-note">
            <span className="note-line" />
            <p>
              <strong>A useful second look, not a safety guarantee.</strong>{" "}
              DTDLINK cannot inspect website content or confirm that a
              destination is legitimate.
            </p>
          </div>
        </>
      )}
    </>
  );
}
