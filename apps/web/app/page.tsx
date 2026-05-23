"use client";

import { Activity, AlertTriangle, Cpu, Database, GitBranch, Mic2, RadioTower, RefreshCw, Send, ShieldCheck } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { compareScenario, getLatestHardwareEvent, getScenario, parseTranscript } from "./api";
import type {
  CompareResponse,
  EmergencyCase,
  HardwareOptimizationEvent,
  OptimizationResult,
  ProcurementSource,
  ProductRequest,
  ScenarioState
} from "./types";

function productLabel(item: ProductRequest | { product_type: string; blood_group?: string | null }) {
  const names: Record<string, string> = {
    PRBC: "PRBC",
    FFP: "FFP",
    platelets: "Platelets",
    tranexamic_acid: "TXA",
    oxytocin: "Oxytocin"
  };
  const group = item.blood_group ? ` ${item.blood_group}` : "";
  return `${group} ${names[item.product_type] ?? item.product_type}`.trim();
}

function ResultCard({ title, result, win }: { title: string; result?: OptimizationResult; win?: boolean }) {
  if (!result) {
    return (
      <div className="result-card">
        <h3>{title}</h3>
        <p className="result-subtitle">Run optimization to populate this plan.</p>
      </div>
    );
  }

  return (
    <div className={`result-card ${win ? "win" : ""}`}>
      <h3>
        {title}
        <span className={`badge ${result.feasible ? "teal" : "amber"}`}>{result.feasible ? "Complete" : "Partial"}</span>
      </h3>
      <p className="result-subtitle">{result.strategy.replaceAll("_", " ")}</p>
      <div className="eta">
        Complete-kit ETA: {result.complete_kit_eta_minutes ? `${result.complete_kit_eta_minutes} min` : "not feasible"}
      </div>
      {result.actions.map((action) => (
        <div className="action-row" key={`${title}-${action.priority_order}-${action.source_id}-${action.product_type}`}>
          <div>
            <b>{action.source_name}</b>
            <span>
              {action.units} x {productLabel(action)} · {action.courier_id || "courier pending"}
            </span>
          </div>
          <span className="badge">{action.eta_minutes}m</span>
        </div>
      ))}
      {result.missing_items.length > 0 && (
        <div className="eta">
          Missing: {result.missing_items.map((item) => `${item.units} x ${productLabel(item)}`).join(", ")}
        </div>
      )}
    </div>
  );
}

function InventoryPanel({ sources }: { sources: ProcurementSource[] }) {
  return (
    <section className="panel dark">
      <div className="panel-header">
        <h2 className="panel-title">
          <Database size={16} /> Source inventory
        </h2>
        <span className="badge amber">{sources.length} sources</span>
      </div>
      <div className="panel-body inventory-list">
        {sources.map((source) => (
          <div className="source-block" key={source.id}>
            <h3>
              {source.name}
              <span className="badge">{source.eta_minutes}m</span>
            </h3>
            {source.inventory.map((item, index) => (
              <div className="inventory-row" key={`${source.id}-${item.product_type}-${index}`}>
                <div>
                  <b>{productLabel(item)}</b>
                  <span>{item.notes || source.source_type.replace("_", " ")}</span>
                </div>
                <span>{item.units_available} units</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}

function metaText(metadata: Record<string, unknown>, key: string) {
  const value = metadata[key];
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return String(value.length);
  return "-";
}

function HardwareFeed({ event }: { event: HardwareOptimizationEvent | null }) {
  const optimized = event?.comparison.optimized;
  const metadata = optimized?.solver_metadata || {};

  return (
    <section className="hardware-band">
      <section className="panel dark">
        <div className="panel-header">
          <h2 className="panel-title">
            <Activity size={16} /> Live hardware feed
          </h2>
          <span className={`badge ${event ? "teal" : "amber"}`}>{event ? "voice received" : "waiting"}</span>
        </div>
        <div className="panel-body hardware-body">
          <div>
            <span className="hardware-label">Latest ESP32 transcript</span>
            <p>{event?.transcript || "Speak into the Elato device to trigger this panel."}</p>
          </div>
          <div className="hardware-stats">
            <div>
              <strong>{metaText(metadata, "qiskit_available")}</strong>
              <span>Qiskit loaded</span>
            </div>
            <div>
              <strong>{metaText(metadata, "solver_type")}</strong>
              <span>solver path</span>
            </div>
            <div>
              <strong>{metaText(metadata, "binary_variables")}</strong>
              <span>binary variables</span>
            </div>
            <div>
              <strong>{optimized?.complete_kit_eta_minutes ? `${optimized.complete_kit_eta_minutes}m` : "-"}</strong>
              <span>optimized ETA</span>
            </div>
          </div>
        </div>
      </section>
    </section>
  );
}

export default function Home() {
  const [scenario, setScenario] = useState<ScenarioState | null>(null);
  const [caseData, setCaseData] = useState<EmergencyCase | null>(null);
  const [transcript, setTranscript] = useState("");
  const [comparison, setComparison] = useState<CompareResponse | null>(null);
  const [hardwareEvent, setHardwareEvent] = useState<HardwareOptimizationEvent | null>(null);
  const [lastHardwareAt, setLastHardwareAt] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getScenario()
      .then((data) => {
        setScenario(data);
        setCaseData(data.case);
        setTranscript(data.case.transcript);
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to load scenario"));
  }, []);

  useEffect(() => {
    const poll = async () => {
      try {
        const event = await getLatestHardwareEvent();
        setHardwareEvent(event);
        if (event && event.received_at !== lastHardwareAt) {
          setLastHardwareAt(event.received_at);
          setTranscript(event.transcript);
          setCaseData(event.comparison.case);
          setComparison(event.comparison);
        }
      } catch {
        // The hardware panel is best-effort; manual demo controls stay usable.
      }
    };
    poll();
    const timer = window.setInterval(poll, 2000);
    return () => window.clearInterval(timer);
  }, [lastHardwareAt]);

  const spokenResponse = useMemo(() => {
    const optimized = comparison?.optimized;
    if (!optimized?.actions.length) return "Run optimization to generate a spoken procurement response.";
    const firstActions = optimized.actions
      .slice(0, 4)
      .map((action) => `${action.units} ${productLabel(action)} from ${action.source_name}`)
      .join("; ");
    return `Procurement plan ready. ${firstActions}. Complete kit ETA ${optimized.complete_kit_eta_minutes} minutes.`;
  }, [comparison]);

  async function handleParse() {
    setBusy(true);
    setError(null);
    try {
      const parsed = await parseTranscript(transcript);
      setCaseData(parsed);
      setComparison(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Parse failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleCompare() {
    if (!scenario || !caseData) return;
    setBusy(true);
    setError(null);
    try {
      setComparison(await compareScenario(caseData, scenario));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Optimization failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <div className="kicker">MatriBlood Q Operations Console</div>
          <h1>Voice to complete-kit procurement in one constrained optimization loop.</h1>
          <p className="subtitle">
            A focused MVP for obstetric emergencies: Elato captures the request, TokenRouter structures it, Qiskit
            chooses the procurement plan, and the dashboard keeps the operator in control.
          </p>
        </div>
        <aside className="status-rack">
          <h2>Phase 2 readiness</h2>
          <div className="status-line">
            <span className="dot good" /> <span>Remote Supabase</span> <b>configured</b>
          </div>
          <div className="status-line">
            <span className="dot good" /> <span>Python/Qiskit API</span> <b>local</b>
          </div>
          <div className="status-line">
            <span className="dot" /> <span>TokenRouter parser</span> <b>fallback-safe</b>
          </div>
          <div className="status-line">
            <span className="dot hot" /> <span>Elato hardware</span> <b>next</b>
          </div>
        </aside>
      </header>

      {error && (
        <div className="panel" style={{ marginBottom: 18 }}>
          <div className="panel-body" style={{ color: "var(--ox)", fontFamily: "ui-sans-serif, Avenir Next, Segoe UI, sans-serif" }}>
            <AlertTriangle size={16} /> {error}
          </div>
        </div>
      )}

      <section className="grid">
        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <Mic2 size={16} /> Emergency transcript
            </h2>
            <span className="badge amber">manual + Elato-ready</span>
          </div>
          <div className="panel-body">
            <textarea className="transcript-box" value={transcript} onChange={(event) => setTranscript(event.target.value)} />
            <div className="button-row">
              <button className="button secondary" onClick={handleParse} disabled={busy}>
                <RefreshCw size={14} /> Parse
              </button>
              <button className="button" onClick={handleCompare} disabled={busy || !caseData}>
                <GitBranch size={14} /> Optimize
              </button>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <ShieldCheck size={16} /> Verified case
            </h2>
            <span className="badge">{caseData?.case_type.replaceAll("_", " ") || "loading"}</span>
          </div>
          <div className="panel-body case-card">
            <div className="case-strip">
              <div className="mini-stat">
                <strong>{caseData?.urgency_score ?? "-"}/10</strong>
                <span>urgency score</span>
              </div>
              <div className="mini-stat teal">
                <strong>{caseData?.target_minutes ?? "-"}m</strong>
                <span>target window</span>
              </div>
            </div>
            <div className="requirements">
              {caseData?.required_products.map((item, index) => (
                <div className="req-row" key={`${item.product_type}-${index}`}>
                  <div>
                    <b>{productLabel(item)}</b>
                    <span>{item.critical ? "critical requested item" : "requested item"}</span>
                  </div>
                  <span className="badge">{item.units} unit{item.units > 1 ? "s" : ""}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <InventoryPanel sources={scenario?.sources || []} />
      </section>

      <HardwareFeed event={hardwareEvent} />

      <section className="quantum-band">
        <div className="formula">
          <strong>Qiskit model</strong>
          <br />
          x_bankA_PRBC = 0/1
          <br />
          x_bankB_platelet = 0/1
          <br />
          x_pharmacyD_oxytocin = 0/1
          <br />
          minimize ETA + missing_penalty + overload - expiry_reward
        </div>

        <section className="panel">
          <div className="panel-header">
            <h2 className="panel-title">
              <Cpu size={16} /> Baseline vs Qiskit
            </h2>
            <span className="badge teal">{comparison?.optimized.solver_metadata.solver_type?.toString() || "ready"}</span>
          </div>
          <div className="panel-body results">
            <ResultCard title="Greedy baseline" result={comparison?.baseline} />
            <ResultCard title="Qiskit optimized" result={comparison?.optimized} win />
          </div>
        </section>

        <section className="panel dark">
          <div className="panel-header">
            <h2 className="panel-title">
              <RadioTower size={16} /> Spoken response
            </h2>
            <span className="badge amber">preview</span>
          </div>
          <div className="panel-body">
            <p style={{ marginTop: 0, fontSize: 24, lineHeight: 1.25 }}>{spokenResponse}</p>
            <button className="button secondary" disabled>
              <Send size={14} /> Send to Elato path
            </button>
          </div>
        </section>
      </section>
    </main>
  );
}
