import hashlib
import hmac

from customer.application.contracts import CustomerCreationFingerprinter


class FakeCustomerCreationFingerprinter(CustomerCreationFingerprinter):
    def fingerprint(self, display_name: str | None) -> str:
        return hmac.new(
            b"test-only-key", (display_name or "").encode("utf-8"), hashlib.sha256
        ).hexdigest()
