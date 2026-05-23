from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .baseline import greedy_nearest_source
from .models import CompareResponse, OptimizeRequest, ParseTranscriptRequest, ParseTranscriptResponse
from .optimizer import optimize_procurement
from .parser import fallback_parse_transcript, parse_with_tokenrouter
from .seed_data import demo_scenario
from .supabase_store import get_supabase, persist_case, persist_comparison, persist_scenario

load_dotenv(".env.local")
load_dotenv()


app = FastAPI(title="MatriBlood Q API", version="0.1.0")

origins = [origin.strip() for origin in os.getenv("API_CORS_ORIGINS", "http://localhost:3000").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/scenario")
def scenario():
    return demo_scenario()


@app.post("/scenario/seed")
def seed_remote_scenario() -> dict[str, str]:
    client = get_supabase()
    if client is None:
        return {"status": "skipped", "reason": "Supabase credentials not configured"}
    persist_scenario(client, demo_scenario())
    return {"status": "ok"}


@app.post("/parse", response_model=ParseTranscriptResponse)
async def parse_transcript(request: ParseTranscriptRequest) -> ParseTranscriptResponse:
    if request.use_tokenrouter:
        try:
            case, raw = await parse_with_tokenrouter(request.transcript)
            client = get_supabase()
            if client:
                persist_case(client, case)
            return ParseTranscriptResponse(case=case, source="tokenrouter_or_fallback", raw_model_output=raw)
        except Exception:
            # Demo resilience: the dashboard can still proceed with deterministic parsing.
            pass
    case = fallback_parse_transcript(request.transcript)
    client = get_supabase()
    if client:
        persist_case(client, case)
    return ParseTranscriptResponse(case=case, source="fallback", raw_model_output=None)


@app.post("/optimize")
def optimize(request: OptimizeRequest):
    return optimize_procurement(
        request.case,
        request.sources,
        request.couriers,
        force_classical_fallback=request.force_classical_fallback,
    )


@app.post("/compare", response_model=CompareResponse)
def compare(request: OptimizeRequest) -> CompareResponse:
    baseline = greedy_nearest_source(request.case, request.sources)
    optimized = optimize_procurement(
        request.case,
        request.sources,
        request.couriers,
        force_classical_fallback=request.force_classical_fallback,
    )
    delta = None
    if baseline.complete_kit_eta_minutes and optimized.complete_kit_eta_minutes:
        delta = baseline.complete_kit_eta_minutes - optimized.complete_kit_eta_minutes
    if optimized.feasible and not baseline.feasible:
        optimized.improvement_summary = "Optimized split procurement completes the kit while the nearest-source baseline is incomplete."
    elif delta is not None and delta > 0:
        optimized.improvement_summary = f"Optimized procurement improves complete-kit ETA by {delta} minutes."
    else:
        optimized.improvement_summary = "Optimized procurement preserves feasibility under the configured constraints."
    comparison = CompareResponse(case=request.case, baseline=baseline, optimized=optimized)
    client = get_supabase()
    if client:
        try:
            persist_case(client, request.case)
            persist_comparison(client, comparison)
        except Exception:
            # Persistence should never break the live demo path.
            pass
    return comparison
