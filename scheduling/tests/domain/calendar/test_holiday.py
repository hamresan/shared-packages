from datetime import date

import pytest

from scheduling.domain.calendar import AnnualClosure


def test_leap_day_closure_applies_only_in_leap_years() -> None:
    closure = AnnualClosure(2, 29)

    assert closure.matches(date(2028, 2, 29))
    assert not closure.matches(date(2027, 2, 28))


def test_annual_closure_rejects_invalid_calendar_date() -> None:
    with pytest.raises(ValueError):
        AnnualClosure(2, 30)


def test_annual_closure_rejects_boolean_fields() -> None:
    with pytest.raises(ValueError):
        AnnualClosure(True, 1)
