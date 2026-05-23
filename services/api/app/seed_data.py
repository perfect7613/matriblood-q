from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import (
    Courier,
    EmergencyCase,
    InventoryItem,
    ProcurementSource,
    ProductRequest,
    ProductType,
    ScenarioState,
    SourceType,
)


DEMO_TRANSCRIPT = (
    "Postpartum hemorrhage emergency. Patient unstable. Need 2 O negative PRBC, "
    "2 FFP, 1 platelet, tranexamic acid and oxytocin within 30 minutes."
)


def demo_scenario() -> ScenarioState:
    expires_today = datetime.now(timezone.utc) + timedelta(hours=8)
    return ScenarioState(
        id="pph-demo-001",
        name="PPH complete-kit procurement demo",
        sources=[
            ProcurementSource(
                id="bank-a",
                name="Blood Bank A",
                source_type=SourceType.BLOOD_BANK,
                eta_minutes=8,
                phone="+91-080-0000-1001",
                inventory=[
                    InventoryItem(product_type=ProductType.PRBC, blood_group="O-", units_available=1),
                    InventoryItem(product_type=ProductType.FFP, blood_group="O-", units_available=2),
                ],
            ),
            ProcurementSource(
                id="bank-b",
                name="Blood Bank B",
                source_type=SourceType.BLOOD_BANK,
                eta_minutes=18,
                phone="+91-080-0000-1002",
                inventory=[
                    InventoryItem(product_type=ProductType.PRBC, blood_group="O-", units_available=1),
                    InventoryItem(
                        product_type=ProductType.PLATELETS,
                        blood_group="O-",
                        units_available=1,
                        expires_at=expires_today,
                        notes="Near-expiry but valid in the demo window",
                    ),
                    InventoryItem(product_type=ProductType.FFP, blood_group="O-", units_available=1),
                ],
            ),
            ProcurementSource(
                id="bank-c",
                name="Blood Bank C",
                source_type=SourceType.BLOOD_BANK,
                eta_minutes=25,
                phone="+91-080-0000-1003",
                inventory=[
                    InventoryItem(product_type=ProductType.PRBC, blood_group="O-", units_available=4),
                    InventoryItem(product_type=ProductType.FFP, blood_group="O-", units_available=4),
                    InventoryItem(product_type=ProductType.PLATELETS, blood_group="O-", units_available=2),
                ],
            ),
            ProcurementSource(
                id="pharmacy-d",
                name="Pharmacy D",
                source_type=SourceType.PHARMACY,
                eta_minutes=14,
                phone="+91-080-0000-2001",
                inventory=[
                    InventoryItem(product_type=ProductType.TXA, units_available=5),
                    InventoryItem(product_type=ProductType.OXYTOCIN, units_available=3),
                ],
            ),
        ],
        couriers=[
            Courier(id="courier-1", name="Courier 1", capacity_units=4),
            Courier(id="courier-2", name="Courier 2", capacity_units=4),
        ],
        case=EmergencyCase(
            id="case-pph-001",
            transcript=DEMO_TRANSCRIPT,
            required_products=[
                ProductRequest(product_type=ProductType.PRBC, blood_group="O-", units=2),
                ProductRequest(product_type=ProductType.FFP, blood_group="O-", units=2),
                ProductRequest(product_type=ProductType.PLATELETS, blood_group="O-", units=1),
                ProductRequest(product_type=ProductType.TXA, units=1),
                ProductRequest(product_type=ProductType.OXYTOCIN, units=1),
            ],
        ),
    )
