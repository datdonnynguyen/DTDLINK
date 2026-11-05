import { lazy, Suspense, useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  ChevronRight,
  Link2,
  Menu,
  ShieldCheck,
  X,
} from "lucide-react";
import { apiRequest } from "./api.js";
import { sessionEntry, validateURL } from "./validation.js";
import CheckPage from "./pages/CheckPage.jsx";
const InsightsPage = lazy(() => import("./pages/InsightsPage.jsx"));
const HowPage = lazy(() => import("./pages/HowPage.jsx"));

const navigation = [
  { path: "/", label: "Check URL", icon: Link2 },
  { path: "/insights", label: "Session insights", icon: BarChart3 },
  { path: "/how-it-works", label: "How it works", icon: BookOpen },
];

export default function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [menuOpen, setMenuOpen] = useState(false);
  const [draft, setDraftState] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [resultURL, setResultURL] = useState("");
  const [history, setHistory] = useState([]);
  const count = useRef(0);
  const inputRef = useRef(null);
  const pageRef = useRef(null);
  const inFlight = useRef(false);

  useEffect(() => {
    const onPop = () => {
      setPath(window.location.pathname);
      setMenuOpen(false);
    };
    const onKey = (event) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("popstate", onPop);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("popstate", onPop);
      window.removeEventListener("keydown", onKey);
    };
  }, []);
  useEffect(() => {
    document.title = `${navigation.find((n) => n.path === path)?.label || "Page not found"} — DTDLINK Preview`;
  }, [path]);

  function navigate(next) {
    if (next !== path) {
      window.history.pushState({}, "", next);
      setPath(next);
    }
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "instant" });
    requestAnimationFrame(() => pageRef.current?.focus());
  }
  function navClick(event, next) {
    if (
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey ||
      event.button !== 0
    )
      return;
    event.preventDefault();
    navigate(next);
  }
  function setDraft(value) {
    setDraftState(value);
    setError(null);
  }
  async function onSubmit(event) {
    event.preventDefault();
    if (inFlight.current) return;
    const validation = validateURL(draft);
    if (validation) {
      setError(validation);
      inputRef.current?.focus();
      return;
    }
    const submittedURL = draft;
    inFlight.current = true;
    setLoading(true);
    setError(null);
    setResult(null);
    setResultURL("");
    try {
      const response = await apiRequest("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: submittedURL }),
      });
      setResult(response);
      setResultURL(submittedURL);
      count.current += 1;
      setHistory((previous) =>
        [...previous, sessionEntry(response, count.current)].slice(-20),
      );
    } catch (failure) {
      setError(failure);
    } finally {
      setLoading(false);
      inFlight.current = false;
    }
  }
  function clearSession() {
    setHistory([]);
    setResult(null);
    setResultURL("");
    setDraftState("");
    count.current = 0;
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <aside
        className={`sidebar ${menuOpen ? "open" : ""}`}
        aria-label="Main navigation"
      >
        <a
          className="brand"
          href="/"
          onClick={(e) => navClick(e, "/")}
          aria-label="DTDLINK home"
        >
          <span className="brand-icon">
            <ShieldCheck size={24} />
          </span>
          <span>
            DTD<span className="brand-light">LINK</span>
            <small>EXPERIMENTAL A3</small>
          </span>
        </a>
        <div className="sidebar-label">WORKSPACE</div>
        <nav>
          {navigation.map((item) => (
            <a
              href={item.path}
              key={item.path}
              onClick={(e) => navClick(e, item.path)}
              aria-current={path === item.path ? "page" : undefined}
              className={`nav-item ${path === item.path ? "active" : ""}`}
            >
              <item.icon size={19} />
              <span>{item.label}</span>
              {path === item.path && <ChevronRight size={16} />}
            </a>
          ))}
        </nav>
      </aside>
      {menuOpen && (
        <button
          className="mobile-overlay"
          aria-label="Close navigation"
          onClick={() => setMenuOpen(false)}
        />
      )}
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="menu-button"
              aria-label={menuOpen ? "Close navigation" : "Open navigation"}
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen(!menuOpen)}
            >
              {menuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>
              {navigation.find((n) => n.path === path)?.label ||
                "Page not found"} · Preview
            </strong>
          </div>
        </header>
        <main id="main-content" ref={pageRef} tabIndex={-1}>
          <Suspense
            fallback={
              <section className="card loading-card" role="status">
                Loading page…
              </section>
            }
          >
            {path === "/" ? (
              <CheckPage
                {...{
                  draft,
                  setDraft,
                  onSubmit,
                  loading,
                  error,
                  result,
                  resultURL,
                }}
                focusRef={inputRef}
                onInsights={() => navigate("/insights")}
              />
            ) : path === "/insights" ? (
              <InsightsPage
                {...{ history, result, loading }}
                onClear={clearSession}
                onCheck={() => navigate("/")}
              />
            ) : path === "/how-it-works" ? (
              <HowPage onCheck={() => navigate("/")} />
            ) : (
              <section className="not-found">
                <span className="error-number">404</span>
                <span className="eyebrow">A LINK WITH NO DESTINATION</span>
                <h1>This page isn’t here.</h1>
                <p>
                  The address may have changed. Your next check is one click
                  away.
                </p>
                <button
                  className="button primary"
                  onClick={() => navigate("/")}
                >
                  Back to Check URL <ArrowRight size={17} />
                </button>
              </section>
            )}
          </Suspense>
        </main>
        <footer className="page-footer">
          <span>
            DTDLINK <span className="footer-dot">·</span> A clearer view before
            you click.
          </span>
          <span>URL text analysis only. No safety guarantees.</span>
        </footer>
      </div>
    </div>
  );
}
