import type { CompareResponse, EmergencyCase, HardwareOptimizationEvent, ScenarioState } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001";

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`API ${path} failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getScenario(): Promise<ScenarioState> {
  return jsonFetch<ScenarioState>("/scenario");
}

export async function parseTranscript(transcript: string): Promise<EmergencyCase> {
  const payload = await jsonFetch<{ case: EmergencyCase }>("/parse", {
    method: "POST",
    body: JSON.stringify({ transcript, use_tokenrouter: true })
  });
  return payload.case;
}

export async function compareScenario(caseData: EmergencyCase, scenario: ScenarioState): Promise<CompareResponse> {
  return jsonFetch<CompareResponse>("/compare", {
    method: "POST",
    body: JSON.stringify({
      case: caseData,
      sources: scenario.sources,
      couriers: scenario.couriers,
      force_classical_fallback: false
    })
  });
}

export async function getLatestHardwareEvent(): Promise<HardwareOptimizationEvent | null> {
  const payload = await jsonFetch<HardwareOptimizationEvent | { status: "idle" }>("/hardware/latest");
  if ("status" in payload) return null;
  return payload;
}
