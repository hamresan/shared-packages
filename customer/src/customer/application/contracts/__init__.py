"""Narrow public protocols at Customer's application boundaries."""

from customer.application.contracts.authorization import CustomerAuthorizer
from customer.application.contracts.clock import Clock
from customer.application.contracts.customer_repository import CustomerRepository
from customer.application.contracts.idempotency_repository import (
    CustomerCreationReceipt,
    CustomerIdempotencyRepository,
)
from customer.application.contracts.identifiers import IdentifierGenerator
from customer.application.contracts.identity_verification import IdentityVerifier
from customer.application.contracts.request_fingerprint import CustomerCreationFingerprinter
from customer.application.contracts.unit_of_work import (
    CustomerUnitOfWork,
    CustomerUnitOfWorkFactory,
)

__all__ = [
    "CustomerAuthorizer",
    "Clock",
    "CustomerCreationFingerprinter",
    "CustomerCreationReceipt",
    "CustomerIdempotencyRepository",
    "CustomerRepository",
    "CustomerUnitOfWork",
    "CustomerUnitOfWorkFactory",
    "IdentityVerifier",
    "IdentifierGenerator",
]
