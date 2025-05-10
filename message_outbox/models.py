import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, Index, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    ...


class BaseModel(Base, AsyncAttrs):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        server_default=func.gen_random_uuid(),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )


class MessageOutbox(BaseModel):
    __tablename__ = "message_outbox"

    topic: Mapped[str] = mapped_column(String, nullable=False)
    trace_id: Mapped[str] = mapped_column(String, nullable=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[str] = mapped_column(String, nullable=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


Index(
    "ix_message_outbox_is_processed",
    MessageOutbox.is_processed,
    postgresql_where=(MessageOutbox.is_processed.is_(False)),
)
