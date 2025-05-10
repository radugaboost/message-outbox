from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from message_outbox.repositories import MessageOutboxRepository
from message_outbox.schemas import MessageBaseSchema

logger = get_logger(__name__)


@dataclass
class MessageOutboxService:
    session: AsyncSession

    async def push_event(
        self, topic: str, payload: dict[str, Any], trace_id: str | None = None
    ) -> None:
        await MessageOutboxRepository(self.session).create(
            MessageBaseSchema(topic=topic, payload=payload, trace_id=trace_id)
        )
