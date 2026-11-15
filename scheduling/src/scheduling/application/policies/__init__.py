"""Authorization and optimistic-version prerequisites for mutations."""

from .calendar_mutation_guard import CalendarMutationGuard

__all__ = ["CalendarMutationGuard"]
