import pytest

from scheduling.domain.time import IanaTimeZone, InvalidTimeZoneError


def test_iana_timezone_preserves_geographical_identity() -> None:
    zone = IanaTimeZone("Asia/Muscat")

    assert zone.key == "Asia/Muscat"
    assert zone.to_zoneinfo().key == "Asia/Muscat"


@pytest.mark.parametrize("name", ["", " UTC", "Invalid/Location", "GMT+4"])
def test_iana_timezone_rejects_invalid_names(name: str) -> None:
    with pytest.raises(InvalidTimeZoneError):
        IanaTimeZone(name)
