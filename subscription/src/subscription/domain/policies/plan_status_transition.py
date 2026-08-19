from subscription.domain.enums.plan import PlanStatus


_ALLOWED_TRANSITIONS: dict[PlanStatus, frozenset[PlanStatus]] = {
    PlanStatus.INACTIVE: frozenset({PlanStatus.ACTIVE, PlanStatus.RETIRED}),
    PlanStatus.ACTIVE: frozenset({PlanStatus.INACTIVE, PlanStatus.RETIRED}),
    PlanStatus.RETIRED: frozenset(),
}


class PlanStatusTransitionPolicy:
    def validate(self, current: PlanStatus, target: PlanStatus) -> None:
        if current == target:
            return
        if target not in _ALLOWED_TRANSITIONS[current]:
            raise ValueError(f"plan status transition {current.value} -> {target.value} is not allowed")
