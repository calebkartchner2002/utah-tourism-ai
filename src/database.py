"""
Database models and configuration for Utah Tourism AI.

Stores recommendation history and user preferences.
"""

import os
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Recommendation(Base):
    """Stores generated travel recommendations."""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    interests: Mapped[str] = mapped_column(String(500))
    duration: Mapped[str] = mapped_column(String(100))
    season: Mapped[str] = mapped_column(String(100))
    activity_level: Mapped[str] = mapped_column(String(100))
    recommendation_text: Mapped[str] = mapped_column(Text)
    used_search: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Recommendation(id={self.id}, interests='{self.interests[:30]}...', created_at={self.created_at})>"


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self):
        # Get database URL from environment
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://utah_user:utah_password@localhost:5432/utah_tourism"
        )

        # Create async engine
        self.engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,  # Verify connections before using
        )

        # Create session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def init_db(self):
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        """Close database connections."""
        await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        async with self.async_session() as session:
            yield session

    async def save_recommendation(
        self,
        interests: str,
        duration: str,
        season: str,
        activity_level: str,
        recommendation_text: str,
        used_search: bool = False
    ) -> Recommendation:
        """Save a recommendation to the database."""
        async with self.async_session() as session:
            recommendation = Recommendation(
                interests=interests,
                duration=duration,
                season=season,
                activity_level=activity_level,
                recommendation_text=recommendation_text,
                used_search=used_search
            )
            session.add(recommendation)
            await session.commit()
            await session.refresh(recommendation)
            return recommendation

    async def get_all_recommendations(self, limit: int = 50) -> list[Recommendation]:
        """Get all recommendations, most recent first."""
        from sqlalchemy import select

        async with self.async_session() as session:
            result = await session.execute(
                select(Recommendation)
                .order_by(Recommendation.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

    async def get_recommendation_by_id(self, recommendation_id: int) -> Recommendation | None:
        """Get a specific recommendation by ID."""
        async with self.async_session() as session:
            return await session.get(Recommendation, recommendation_id)
