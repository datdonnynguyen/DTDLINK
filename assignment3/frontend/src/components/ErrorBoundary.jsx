import { Component } from "react";
import { ShieldAlert, ArrowRight } from "lucide-react";

export class ErrorBoundary extends Component {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed)
      return (
        <main className="standalone-error">
          <ShieldAlert size={48} aria-hidden="true" />
          <p className="eyebrow">LET’S START AGAIN</p>
          <h1>Something unexpected happened.</h1>
          <p>
            Your checks have not been saved. Reload to start a fresh session.
          </p>
          <a className="button primary" href="/">
            Reload DTDLINK <ArrowRight size={18} />
          </a>
        </main>
      );
    return this.props.children;
  }
}
