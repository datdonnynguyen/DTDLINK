import {
  ArrowRight,
  Braces,
  Cpu,
  Link2,
  LockKeyhole,
  ShieldCheck,
} from "lucide-react";

export default function HowPage({ onCheck }) {
  const steps = [
    {
      icon: Link2,
      title: "You provide a complete URL.",
      text: "The interface checks the format before sending it to your local FastAPI service. The backend independently validates it again.",
    },
    {
      icon: Braces,
      title: "We read its text, not its website.",
      text: "The same A2 feature extractor measures 36 properties, including length, host structure, encoding and account-related tokens. No DNS lookup or page request is made.",
    },
    {
      icon: Cpu,
      title: "The saved model makes a prediction.",
      text: "An experimental A3 classifier combines short character patterns with 36 URL measurements. Its train/inference formatting rules match. It returns a probability for the combined phishing, malware and defacement class. At 50% or above, the predicted class is potentially dangerous.",
    },
    {
      icon: ShieldCheck,
      title: "You get evidence and a next step.",
      text: "We display the predicted label, its confidence, observed URL signals and practical guidance. Scores between 40% and 60% receive an additional uncertainty notice; this is a presentation rule, not calibrated uncertainty.",
    },
  ];
  return (
    <>
      <div className="page-heading compact">
        <div>
          <span className="eyebrow">A LOOK UNDER THE HOOD</span>
          <h1>
            No mystery.
            <br />
            <span>Just a closer look.</span>
          </h1>
          <p>Understand what DTDLINK does, and where its view ends.</p>
        </div>
        <span className="subtle-badge">
          <LockKeyhole size={14} /> Offline by design
        </span>
      </div>
      <div className="how-layout">
        <section className="card process-card">
          <span className="eyebrow">FROM INPUT TO INSIGHT</span>
          {steps.map((step, i) => (
            <article className="process-step" key={step.title}>
              <div className="step-marker">
                <step.icon size={22} />
                {i < steps.length - 1 && <span />}
              </div>
              <div>
                <span className="eyebrow">STEP 0{i + 1}</span>
                <h2>{step.title}</h2>
                <p>{step.text}</p>
              </div>
            </article>
          ))}
        </section>
        <aside className="how-aside">
          <section className="card">
            <span className="eyebrow">THE MODEL</span>
            <h2>Separate A3 experiment.</h2>
            <dl className="model-spec">
              <div>
                <dt>Method</dt>
                <dd>TF-IDF + logistic regression</dd>
              </div>
              <div>
                <dt>Input</dt>
                <dd>Text patterns + 36 measures</dd>
              </div>
              <div>
                <dt>Classes</dt>
                <dd>Benign / combined dangerous</dd>
              </div>
              <div>
                <dt>Threshold</dt>
                <dd>0.5</dd>
              </div>
              <div>
                <dt>Inference</dt>
                <dd>Local, no destination access</dd>
              </div>
            </dl>
          </section>
          <section className="card limitations-card">
            <span className="eyebrow">KNOW THE LIMITS</span>
            <h2>A prediction has limits.</h2>
            <ul>
              <li>
                The model cannot distinguish phishing from malware or
                defacement.
              </li>
              <li>Confidence values are uncalibrated estimates.</li>
              <li>Formatting and encoding can change predictions.</li>
              <li>
                Benign predictions can miss dangerous URLs; dangerous
                predictions can be false alarms.
              </li>
              <li>
                No page content, domain reputation, ownership or certificate is
                checked.
              </li>
            </ul>
          </section>
        </aside>
      </div>
      <div className="how-cta">
        <div>
          <h2>Make your next click an informed one.</h2>
          <p>Start with a link. Keep the bigger picture in mind.</p>
        </div>
        <button className="button primary" onClick={onCheck}>
          Check a URL <ArrowRight size={17} />
        </button>
      </div>
    </>
  );
}
