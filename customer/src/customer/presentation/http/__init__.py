"""Optional FastAPI integration (install the ``fastapi`` extra)."""

from customer.presentation.http.router import create_customer_router

__all__ = ["create_customer_router"]
