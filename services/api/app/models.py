from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProductType(str, Enum):
    PRBC = "PRBC"
    FFP = "FFP"
    PLATELETS = "platelets"
    TXA = "tranexamic_acid"
    OXYTOCIN = "oxytocin"


class SourceType(str, Enum):
    BLOOD_BANK = "blood_bank"
    PHARMACY = "pharmacy"


class ProductRequest(BaseModel):
    product_type: ProductType
    blood_group: Optional[str] = None
    units: int = Field(ge=1)
    critical: bool = True


class InventoryItem(BaseModel):
    product_type: ProductType
    blood_group: Optional[str] = None
    units_available: int = Field(ge=0)
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None


class ProcurementSource(BaseModel):
    id: str
    name: str
    source_type: SourceType
    eta_minutes: int = Field(ge=0)
    phone: Optional[str] = None
    is_tie_up_partner: bool = True
    inventory: List[InventoryItem]


class Courier(BaseModel):
    id: str
    name: str
    capacity_units: int = Field(ge=1)
    available: bool = True


class EmergencyCase(BaseModel):
    id: str
    transcript: str
    case_type: str = "postpartum_hemorrhage"
    patient_status: str = "unstable"
    target_minutes: int = Field(default=30, ge=1)
    urgency_score: int = Field(default=10, ge=1, le=10)
    required_products: List[ProductRequest]
    missing_fields: List[str] = Field(default_factory=list)
    parser_confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ScenarioState(BaseModel):
    id: str
    name: str
    sources: List[ProcurementSource]
    couriers: List[Courier]
    case: EmergencyCase


class ProcurementAction(BaseModel):
    source_id: str
    source_name: str
    product_type: ProductType
    blood_group: Optional[str] = None
    units: int = Field(ge=1)
    eta_minutes: int = Field(ge=0)
    priority_order: int
    courier_id: Optional[str] = None
    reason: str


class OptimizationResult(BaseModel):
    strategy: str
    feasible: bool
    complete_kit_eta_minutes: Optional[int]
    missing_items: List[ProductRequest]
    actions: List[ProcurementAction]
    objective_value: float
    solver_metadata: Dict[str, Any] = Field(default_factory=dict)
    improvement_summary: Optional[str] = None


class ParseTranscriptRequest(BaseModel):
    transcript: str
    use_tokenrouter: bool = True


class ParseTranscriptResponse(BaseModel):
    case: EmergencyCase
    source: str
    raw_model_output: Optional[Dict[str, Any]] = None


class OptimizeRequest(BaseModel):
    case: EmergencyCase
    sources: List[ProcurementSource]
    couriers: List[Courier]
    force_classical_fallback: bool = False


class CompareResponse(BaseModel):
    case: EmergencyCase
    baseline: OptimizationResult
    optimized: OptimizationResult


class HardwareVoiceRequest(BaseModel):
    transcript: str


class HardwareOptimizationEvent(BaseModel):
    transcript: str
    received_at: datetime
    comparison: CompareResponse
