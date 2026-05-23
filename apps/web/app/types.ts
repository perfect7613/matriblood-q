export type ProductType = "PRBC" | "FFP" | "platelets" | "tranexamic_acid" | "oxytocin";

export type ProductRequest = {
  product_type: ProductType;
  blood_group?: string | null;
  units: number;
  critical: boolean;
};

export type InventoryItem = {
  product_type: ProductType;
  blood_group?: string | null;
  units_available: number;
  expires_at?: string | null;
  notes?: string | null;
};

export type ProcurementSource = {
  id: string;
  name: string;
  source_type: "blood_bank" | "pharmacy";
  eta_minutes: number;
  phone?: string | null;
  is_tie_up_partner: boolean;
  inventory: InventoryItem[];
};

export type Courier = {
  id: string;
  name: string;
  capacity_units: number;
  available: boolean;
};

export type EmergencyCase = {
  id: string;
  transcript: string;
  case_type: string;
  patient_status: string;
  target_minutes: number;
  urgency_score: number;
  required_products: ProductRequest[];
  missing_fields: string[];
  parser_confidence: number;
};

export type ProcurementAction = {
  source_id: string;
  source_name: string;
  product_type: ProductType;
  blood_group?: string | null;
  units: number;
  eta_minutes: number;
  priority_order: number;
  courier_id?: string | null;
  reason: string;
};

export type OptimizationResult = {
  strategy: string;
  feasible: boolean;
  complete_kit_eta_minutes?: number | null;
  missing_items: ProductRequest[];
  actions: ProcurementAction[];
  objective_value: number;
  solver_metadata: Record<string, unknown>;
  improvement_summary?: string | null;
};

export type ScenarioState = {
  id: string;
  name: string;
  sources: ProcurementSource[];
  couriers: Courier[];
  case: EmergencyCase;
};

export type CompareResponse = {
  case: EmergencyCase;
  baseline: OptimizationResult;
  optimized: OptimizationResult;
};
