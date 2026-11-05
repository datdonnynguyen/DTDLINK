import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";
import { ArrowUpRight, BarChart3, MousePointer2 } from "lucide-react";

const categories = {
  high: "High attention",
  medium: "Medium attention",
  low: "Context",
};
const colors = {
  high: "var(--danger)",
  medium: "var(--warning)",
  low: "var(--chart-context)",
};
const tooltipStyle = {
  backgroundColor: "var(--surface-raised)",
  border: "1px solid var(--line-strong)",
  color: "var(--foreground)",
  borderRadius: 10,
  fontSize: 12,
};

export function SignalChart({ result }) {
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState(null);
  const signals = result.signals.filter(
    (s) => s.present && (filter === "all" || s.severity === filter),
  );
  const data = ["high", "medium", "low"]
    .filter((level) => filter === "all" || filter === level)
    .map((level) => ({
      name: categories[level],
      count: signals.filter((s) => s.severity === level).length,
      level,
    }));
  const current = result.signals.find((s) => s.id === selected);
  return (
    <section className="card chart-card" aria-labelledby="signal-chart-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">CURRENT RESULT</span>
          <h2 id="signal-chart-title">What deserves a closer look?</h2>
        </div>
        <BarChart3 size={21} aria-hidden="true" />
      </div>
      <p className="muted">
        Observed URL signals by attention level. These are rules, not model
        contribution scores.
      </p>
      <label className="select-label" htmlFor="signal-filter">
        Show signals
        <select
          id="signal-filter"
          value={filter}
          onChange={(e) => {
            setFilter(e.target.value);
            setSelected(null);
          }}
        >
          <option value="all">All attention levels</option>
          <option value="high">High attention</option>
          <option value="medium">Medium attention</option>
          <option value="low">Context</option>
        </select>
      </label>
      <div
        className="chart-frame"
        aria-label="Bar chart of observed signal counts"
      >
        <ResponsiveContainer width="100%" height={210}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ left: 0, right: 28, top: 8, bottom: 4 }}
            accessibilityLayer
          >
            <CartesianGrid
              strokeDasharray="3 4"
              horizontal={false}
              stroke="var(--line)"
            />
            <XAxis
              type="number"
              allowDecimals={false}
              domain={[0, Math.max(1, ...data.map((d) => d.count))]}
              tick={{ fontSize: 12, fill: "var(--muted)" }}
            />
            <YAxis
              dataKey="name"
              type="category"
              width={110}
              tick={{ fontSize: 12, fill: "var(--muted)" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={tooltipStyle}
              itemStyle={{ color: "var(--foreground)" }}
              labelStyle={{ color: "var(--foreground)" }}
              formatter={(value) => [`${value} observed`, "Signals"]}
              cursor={{ fill: "var(--surface-raised)" }}
            />
            <Bar
              dataKey="count"
              name="Signals"
              barSize={22}
              radius={[0, 5, 5, 0]}
              label={{
                position: "right",
                fontSize: 12,
                fill: "var(--foreground)",
              }}
            >
              {data.map((row) => (
                <Cell key={row.level} fill={colors[row.level]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="legend">High attention · Medium attention · Context</div>
      <div className="signal-buttons">
        {signals.map((signal) => (
          <button
            className={`signal-chip ${selected === signal.id ? "selected" : ""}`}
            key={signal.id}
            aria-pressed={selected === signal.id}
            onClick={() => setSelected(signal.id)}
          >
            <span className={`signal-dot ${signal.severity}`} />
            {signal.title}
            <ArrowUpRight size={13} />
          </button>
        ))}
      </div>
      {signals.length === 0 && (
        <p className="empty-note">
          No observed signals in this category. This does not establish safety.
        </p>
      )}
      <div className="chart-detail" aria-live="polite">
        {current ? (
          <>
            <strong>{current.title}</strong>
            <p>{current.detail}</p>
          </>
        ) : (
          <>
            <MousePointer2 size={16} aria-hidden="true" />
            <span>Select a signal above to understand what it means.</span>
          </>
        )}
      </div>
    </section>
  );
}

export function SessionChart({ history }) {
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState(null);
  const data = history.filter(
    (entry) => filter === "all" || entry.predictedClass === Number(filter),
  );
  const current = history.find((entry) => entry.number === selected);
  return (
    <section className="card chart-card" aria-labelledby="session-chart-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">THIS SESSION</span>
          <h2 id="session-chart-title">How do your checks compare?</h2>
        </div>
        <BarChart3 size={21} aria-hidden="true" />
      </div>
      <p className="muted">
        Compare model risk scores. Only anonymous scores stay in memory; URLs
        are excluded.
      </p>
      <label className="select-label" htmlFor="session-filter">
        Filter checks
        <select
          id="session-filter"
          value={filter}
          onChange={(e) => {
            setFilter(e.target.value);
            setSelected(null);
          }}
        >
          <option value="all">All results</option>
          <option value="1">Potentially dangerous</option>
          <option value="0">Likely legitimate</option>
        </select>
      </label>
      {data.length ? (
        <>
          <div
            className="chart-frame"
            aria-label="Bar chart of model risk scores by anonymous check number"
          >
            <ResponsiveContainer width="100%" height={230}>
              <BarChart
                data={data}
                margin={{ left: 0, right: 10, top: 12, bottom: 6 }}
                accessibilityLayer
              >
                <CartesianGrid
                  strokeDasharray="3 4"
                  vertical={false}
                  stroke="var(--line)"
                />
                <XAxis
                  dataKey="number"
                  tickFormatter={(n) => `#${n}`}
                  tick={{ fontSize: 12, fill: "var(--muted)" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={[0, 100]}
                  width={35}
                  unit="%"
                  tick={{ fontSize: 11, fill: "var(--muted)" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  itemStyle={{ color: "var(--foreground)" }}
                  labelStyle={{ color: "var(--foreground)" }}
                  formatter={(value) => [`${value}%`, "Model risk score"]}
                  labelFormatter={(n) => `Check #${n}`}
                  cursor={{ fill: "var(--surface-raised)" }}
                />
                <ReferenceLine
                  y={50}
                  stroke="var(--muted)"
                  strokeDasharray="5 4"
                />
                <Bar
                  dataKey="score"
                  name="Model risk score"
                  maxBarSize={36}
                  radius={[5, 5, 0, 0]}
                  label={{
                    position: "top",
                    fontSize: 11,
                    fill: "var(--foreground)",
                    formatter: (v) => `${v}%`,
                  }}
                >
                  {data.map((row) => (
                    <Cell
                      key={row.number}
                      fill={
                        row.predictedClass ? "var(--danger)" : "var(--success)"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="legend">
            <span className="signal-dot high" />
            Potentially dangerous <span className="signal-dot low" />
            Likely legitimate <span>Dashed line: 50% decision threshold</span>
          </div>
          <div className="check-selectors" aria-label="Select check details">
            {data.map((entry) => (
              <button
                key={entry.number}
                aria-pressed={selected === entry.number}
                className={`check-selector ${selected === entry.number ? "selected" : ""}`}
                onClick={() => setSelected(entry.number)}
              >
                Check #{entry.number}
              </button>
            ))}
          </div>
        </>
      ) : (
        <div className="empty-chart">
          <BarChart3 size={32} aria-hidden="true" />
          <strong>
            {history.length
              ? "No checks match this filter."
              : "Your first check starts the story."}
          </strong>
          <p>
            {history.length
              ? "Choose another result type."
              : "Analyse a URL to see anonymous scores here."}
          </p>
        </div>
      )}
      <div className="chart-detail" aria-live="polite">
        {current ? (
          <span>
            <strong>
              Check #{current.number} · {current.label}
            </strong>
            <br />
            Model score {current.score}% · Predicted-class confidence{" "}
            {current.confidence}% · {current.signals} observed signals
          </span>
        ) : (
          <>
            <MousePointer2 size={16} aria-hidden="true" />
            <span>Select a check to inspect its score and signal count.</span>
          </>
        )}
      </div>
    </section>
  );
}
