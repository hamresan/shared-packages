from identity.presentation.ip_address import IpAddressNormalizer


def test_ipv6_variants_normalize_to_same_requester_key() -> None:
    normalizer = IpAddressNormalizer()

    expanded = normalizer.normalize("2001:0db8:0000:0000:0000:0000:0000:0001")
    compressed = normalizer.normalize("2001:db8::1")

    assert expanded == "2001:db8::1"
    assert compressed == expanded


def test_ipv4_address_is_canonicalized() -> None:
    normalizer = IpAddressNormalizer()

    assert normalizer.normalize(" 203.0.113.10 ") == "203.0.113.10"


def test_invalid_ip_address_is_rejected() -> None:
    normalizer = IpAddressNormalizer()

    assert normalizer.normalize("not-an-ip") is None
