import pytest

from subscription import PlanStatus, PlanStatusTransitionPolicy


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (PlanStatus.INACTIVE, PlanStatus.ACTIVE),
        (PlanStatus.INACTIVE, PlanStatus.RETIRED),
        (PlanStatus.ACTIVE, PlanStatus.INACTIVE),
        (PlanStatus.ACTIVE, PlanStatus.RETIRED),
        (PlanStatus.ACTIVE, PlanStatus.ACTIVE),
    ],
)
def test_plan_status_transition_policy_allows_valid_transitions(
    current: PlanStatus,
    target: PlanStatus,
) -> None:
    PlanStatusTransitionPolicy().validate(current, target)


@pytest.mark.parametrize("target", [PlanStatus.ACTIVE, PlanStatus.INACTIVE])
def test_plan_status_transition_policy_rejects_transition_from_retired(
    target: PlanStatus,
) -> None:
    with pytest.raises(ValueError, match="not allowed"):
        PlanStatusTransitionPolicy().validate(PlanStatus.RETIRED, target)
