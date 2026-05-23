from app.models import ProductType
from app.parser import fallback_parse_transcript


def test_fallback_parser_extracts_pph_products():
    case = fallback_parse_transcript(
        "PPH emergency unstable, need 2 O negative PRBC, 2 FFP, 1 platelet, TXA and oxytocin within 30 minutes"
    )

    assert case.case_type == "postpartum_hemorrhage"
    assert case.patient_status == "unstable"
    assert case.target_minutes == 30
    assert {item.product_type for item in case.required_products} == {
        ProductType.PRBC,
        ProductType.FFP,
        ProductType.PLATELETS,
        ProductType.TXA,
        ProductType.OXYTOCIN,
    }
    prbc = next(item for item in case.required_products if item.product_type == ProductType.PRBC)
    assert prbc.units == 2
    assert prbc.blood_group == "O-"
