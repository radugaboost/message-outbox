from dataclasses import dataclass
from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from message_outbox.models import MessageOutbox
from message_outbox.schemas import MessageBaseSchema


@dataclass
class MessageOutboxRepository:
    session: AsyncSession

    async def create(self, message: MessageBaseSchema) -> MessageOutbox:
        new_message = MessageOutbox(**message.model_dump())
        self.session.add(new_message)

        return new_message

    async def get(self, limit: int = 500) -> Sequence[MessageOutbox]:
        return (
            await self.session.scalars(
                select(MessageOutbox)
                .where(MessageOutbox.is_processed.is_(False))
                .order_by(MessageOutbox.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
        ).all()

    async def batch_mark_processed(self, ids: list[UUID]) -> None:
        await self.session.execute(
            update(MessageOutbox).where(MessageOutbox.id.in_(ids)).values(is_processed=True)
        )
