"""Boundary validation of availability requests and trusted calendar snapshots."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from scheduling.domain.calendar import CalendarScope

if TYPE_CHECKING:
    from .models import AvailabilityRequest


def validate_availability_request(request: AvailabilityRequest) -> None:
    if request.organization.scope is not CalendarScope.ORGANIZATION:
        raise ValueError("Organization calendar must have organization scope.")
    if request.location.scope is not CalendarScope.LOCATION:
        raise ValueError("Location calendar must have location scope.")
    if any(resource.scope is not CalendarScope.RESOURCE for resource in request.resources):
        raise ValueError("Every eligible resource must have a resource calendar.")
    tenant_ids = {
        calendar.tenant_id
        for calendar in (request.organization, request.location, *request.resources)
    }
    if len(tenant_ids) != 1:
        raise ValueError("All calendars must belong to one trusted tenant.")
    resource_ids = [resource.scope_id for resource in request.resources]
    if len(resource_ids) != len(set(resource_ids)):
        raise ValueError("Resource identifiers must be unique.")
    if len(request.resources) > 100:
        raise ValueError("A single query supports at most 100 resources.")
    if request.query_window.end - request.query_window.start > timedelta(days=31):
        raise ValueError("Availability searches cannot exceed 31 days.")
    if request.now.tzinfo is None or request.now.utcoffset() != timedelta():
        raise ValueError("now must be an aware UTC instant.")
    if request.duration < timedelta(minutes=1) or request.step < timedelta(minutes=1):
        raise ValueError("Duration and step must each be at least one minute.")
    if any(
        value < timedelta()
        for value in (request.buffer_before, request.buffer_after, request.minimum_notice)
    ):
        raise ValueError("Buffers and minimum notice cannot be negative.")
    if request.maximum_horizon <= timedelta():
        raise ValueError("Maximum horizon must be positive.")
    if any(busy.resource_id not in resource_ids for busy in request.busy_intervals):
        raise ValueError("Busy intervals must refer to eligible resources in this query.")
