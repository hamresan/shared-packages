"""Replay-protection application errors."""


class ReplayProtectionError(Exception):
    """Base error for replay-protection failures."""


class TimestampOutsideToleranceError(ReplayProtectionError):
    """Raised when a signed request timestamp is outside the allowed skew."""


class ReplayDetectedError(ReplayProtectionError):
    """Raised when a client nonce has already been consumed."""
