from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerCreationFingerprinter,
    CustomerCreationReceipt,
    CustomerUnitOfWorkFactory,
    IdentifierGenerator,
)
from customer.application.factories import CustomerFactory
from customer.application.mapping import CustomerResultMapper
from customer.application.models import CreateCustomerCommand, CustomerResult
from customer.application.permissions import CustomerPermission
from customer.application.policies import CustomerScopePolicy
from customer.application.validation import CustomerNameValidator
from customer.domain.errors import (
    CustomerIdempotencyConflictError,
    CustomerNotFoundError,
    CustomerValidationError,
)


class CreateCustomerService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        authorizer: CustomerAuthorizer,
        scope: CustomerScopePolicy,
        validator: CustomerNameValidator,
        customer_factory: CustomerFactory,
        ids: IdentifierGenerator,
        clock: Clock,
        mapper: CustomerResultMapper,
        fingerprinter: CustomerCreationFingerprinter,
    ) -> None:
        self.uow = uow
        self.authorizer = authorizer
        self.scope = scope
        self.validator = validator
        self.customer_factory = customer_factory
        self.ids = ids
        self.clock = clock
        self.mapper = mapper
        self.fingerprinter = fingerprinter

    async def execute(self, command: CreateCustomerCommand) -> CustomerResult:
        self.scope.require_matching_business(command.business_id, command.actor)
        await self.authorizer.require_permission(command.actor, CustomerPermission.CREATE)
        name = self.validator.normalize(command.display_name)
        if command.idempotency_key is not None and not (0 < len(command.idempotency_key) <= 200):
            raise CustomerValidationError("Invalid idempotency key")

        fingerprint = self.fingerprinter.fingerprint(name)
        async with self.uow(command.business_id) as transaction:
            if command.idempotency_key is not None:
                await transaction.idempotency.lock_key(command.business_id, command.idempotency_key)
                existing = await transaction.idempotency.find(
                    command.business_id, command.idempotency_key
                )
                if existing is not None:
                    if existing.fingerprint != fingerprint:
                        raise CustomerIdempotencyConflictError("Idempotency key already used")
                    customer = await transaction.customers.get(
                        command.business_id, existing.customer_id
                    )
                    if customer is None:
                        raise CustomerNotFoundError("Customer is unavailable")
                    return self.mapper.to_result(customer)

            customer = self.customer_factory.create(
                self.ids.new_id(), command.business_id, name, self.clock.now()
            )
            await transaction.customers.add(customer)
            if command.idempotency_key is not None:
                await transaction.idempotency.add(
                    CustomerCreationReceipt(
                        command.business_id, command.idempotency_key, fingerprint, customer.id
                    )
                )
            await transaction.commit_audited(command.actor, "customer.create", customer.id)
            return self.mapper.to_result(customer)
