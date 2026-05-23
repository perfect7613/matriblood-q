from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional

import httpx

from .models import EmergencyCase, ProductRequest, ProductType


def normalize_blood_group(text: str) -> Optional[str]:
    t = text.lower().replace(" ", "").replace("negative", "-").replace("positive", "+")
    if "o-" in t or "oneg" in t:
        return "O-"
    if "o+" in t:
        return "O+"
    if "a+" in t:
        return "A+"
    if "b+" in t:
        return "B+"
    if "ab+" in t:
        return "AB+"
    return None


def fallback_parse_transcript(transcript: str) -> EmergencyCase:
    lower = transcript.lower()
    blood_group = normalize_blood_group(transcript) or "O-"
    target_match = re.search(r"within\s+(\d+)\s*minutes?", lower)
    target_minutes = int(target_match.group(1)) if target_match else 30

    def units_before(*terms: str, default: int = 1) -> int:
        for term in terms:
            match = re.search(rf"(\d+)\s+(?:{term})", lower)
            if match:
                return int(match.group(1))
        return default

    required = [
        ProductRequest(
            product_type=ProductType.PRBC,
            blood_group=blood_group,
            units=units_before("o negative prbc", "o-negative prbc", "prbc", "packed cells", default=2),
        ),
        ProductRequest(
            product_type=ProductType.FFP,
            blood_group=blood_group,
            units=units_before("ffp", default=2),
        ),
        ProductRequest(
            product_type=ProductType.PLATELETS,
            blood_group=blood_group,
            units=units_before("platelet", "platelets", default=1),
        ),
    ]
    if "tranexamic" in lower or "txa" in lower:
        required.append(ProductRequest(product_type=ProductType.TXA, units=1))
    if "oxytocin" in lower:
        required.append(ProductRequest(product_type=ProductType.OXYTOCIN, units=1))

    missing = []
    if not blood_group:
        missing.append("blood_group")
    return EmergencyCase(
        id="case-from-transcript",
        transcript=transcript,
        case_type="postpartum_hemorrhage" if "hemorrhage" in lower or "haemorrhage" in lower or "pph" in lower else "obstetric_emergency",
        patient_status="unstable" if "unstable" in lower else "unknown",
        target_minutes=target_minutes,
        urgency_score=10 if "unstable" in lower or "emergency" in lower else 8,
        required_products=required,
        missing_fields=missing,
        parser_confidence=0.72,
    )


def _normalize_model_json(payload: Dict[str, Any], transcript: str) -> EmergencyCase:
    products = []
    for item in payload.get("required_products", []):
        product = str(item.get("product_type", "")).lower()
        product_type = {
            "prbc": ProductType.PRBC,
            "packed_cells": ProductType.PRBC,
            "packed red blood cells": ProductType.PRBC,
            "ffp": ProductType.FFP,
            "platelets": ProductType.PLATELETS,
            "platelet": ProductType.PLATELETS,
            "tranexamic_acid": ProductType.TXA,
            "txa": ProductType.TXA,
            "oxytocin": ProductType.OXYTOCIN,
        }.get(product, ProductType.PRBC)
        products.append(
            ProductRequest(
                product_type=product_type,
                blood_group=item.get("blood_group"),
                units=max(1, int(item.get("units", 1))),
            )
        )

    if not products:
        return fallback_parse_transcript(transcript)

    return EmergencyCase(
        id="case-from-tokenrouter",
        transcript=transcript,
        case_type=payload.get("case_type", "postpartum_hemorrhage"),
        patient_status=payload.get("patient_status", "unknown"),
        target_minutes=int(payload.get("target_minutes", 30)),
        urgency_score=int(payload.get("urgency_score", 9)),
        required_products=products,
        missing_fields=payload.get("missing_fields", []),
        parser_confidence=float(payload.get("confidence", 0.85)),
    )


async def parse_with_tokenrouter(transcript: str) -> tuple[EmergencyCase, Optional[Dict[str, Any]]]:
    api_key = os.getenv("TOKENROUTER_API_KEY")
    if not api_key:
        return fallback_parse_transcript(transcript), None

    base_url = os.getenv("TOKENROUTER_BASE_URL", "https://api.tokenrouter.io").rstrip("/")
    model = os.getenv("TOKENROUTER_MODEL", "openai/gpt-4.1-mini")
    prompt = (
        "Extract obstetric emergency procurement requirements as strict JSON. "
        "Do not decide treatment. Use product_type values only: PRBC, FFP, platelets, "
        "tranexamic_acid, oxytocin. Include blood_group when spoken, units, target_minutes, "
        "urgency_score, missing_fields, confidence.\n\nTranscript:\n"
        f"{transcript}"
    )

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            f"{base_url}/v1/responses",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "input": prompt,
                "text": {"format": {"type": "json_object"}},
            },
        )
        response.raise_for_status()
        raw = response.json()

    text = raw.get("output_text")
    if not text:
        chunks = raw.get("output", [])
        text_parts = []
        for chunk in chunks:
            for content in chunk.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    text_parts.append(content.get("text", ""))
        text = "\n".join(text_parts)
    try:
        data = json.loads(text or "{}")
    except json.JSONDecodeError:
        return fallback_parse_transcript(transcript), {"unparsed_response": raw}

    return _normalize_model_json(data, transcript), raw
