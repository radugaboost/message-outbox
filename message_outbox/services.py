from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from message_outbox.repositories import MessageOutboxRepository
from message_outbox.schemas import MessageBaseSchema

logger = get_logger(__name__)


@dataclass
class MessageOutboxService:
    session: AsyncSession

    async def push_event(
        self, topic: str, event_type: str, payload: str, trace_id: str | None = None
    ) -> None:
        await MessageOutboxRepository(self.session).create(
            MessageBaseSchema(
                topic=topic, event_type=event_type, payload=payload, trace_id=trace_id
            )
        )
