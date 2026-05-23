from __future__ import annotations

from .models import InventoryItem, ProductRequest, ProductType


def is_compatible(request: ProductRequest, item: InventoryItem) -> bool:
    if request.product_type != item.product_type:
        return False

    if request.product_type in {ProductType.TXA, ProductType.OXYTOCIN}:
        return True

    if request.blood_group == item.blood_group:
        return True

    # MVP emergency simplification: O- PRBC can satisfy an urgent PRBC request.
    if request.product_type == ProductType.PRBC and item.blood_group == "O-":
        return True

    return False
