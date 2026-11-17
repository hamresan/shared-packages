"""Canonical contact value validation; never serves as identity verification."""

import re

from customer.domain.contact import ContactKind
from customer.domain.errors import CustomerValidationError


class ContactValueNormalizer:
    def normalize(self, kind: ContactKind, value: str) -> str:
        candidate = value.strip()
        if kind is ContactKind.EMAIL:
            if len(candidate) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", candidate):
                raise CustomerValidationError("Invalid email contact")
            return candidate.casefold()
        if kind is ContactKind.PHONE:
            if not re.fullmatch(r"\+[1-9][0-9]{7,14}", candidate):
                raise CustomerValidationError("Phone contact must use E.164 format")
            return candidate
        raise CustomerValidationError("Unsupported contact kind")
