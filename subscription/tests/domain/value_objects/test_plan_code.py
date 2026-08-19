import pytest

from subscription import PlanCode


@pytest.mark.parametrize("code", ["free", "pro", "business_v2", "analytics.addon", "ai-addon"])
def test_plan_code_accepts_canonical_identifiers(code: str) -> None:
    assert PlanCode(code).value == code


@pytest.mark.parametrize("code", ["", "Pro", "pro plan", "_pro", "pro/plan", "a" * 65])
def test_plan_code_rejects_non_canonical_identifiers(code: str) -> None:
    with pytest.raises(ValueError, match="plan code"):
        PlanCode(code)
