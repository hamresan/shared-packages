from ipaddress import ip_address


class IpAddressNormalizer:
    def normalize(self, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return ip_address(value.strip()).compressed
        except ValueError:
            return None


__all__ = ["IpAddressNormalizer"]
