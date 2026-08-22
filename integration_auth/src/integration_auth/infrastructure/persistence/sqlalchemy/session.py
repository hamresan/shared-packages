"""Shared SQLAlchemy async-session typing."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

AsyncSessionFactory = async_sessionmaker[AsyncSession]
