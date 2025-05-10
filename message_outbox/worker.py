from asyncio import gather, sleep
from json import dumps

from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from message_outbox.repositories import MessageOutboxRepository

logger = get_logger(__name__)


class MessageOutboxWorker:
    def __init__(self, session: AsyncSession, producer: AIOKafkaProducer, timeout: int = 2) -> None:
        self.session = session
        self.producer = producer
        self.timeout = timeout

    async def process_events(self) -> None:
        outbox_repository = MessageOutboxRepository(self.session)

        logger.info("Starting event outbox worker")
        while True:
            messages = await outbox_repository.get()
            if not messages:
                await sleep(self.timeout)
                continue

            try:
                send_message_tasks = []
                message_ids = []

                for message in messages:
                    headers = [
                        ("x-message-id", str(message.id).encode("utf-8")),
                    ]

                    if message.trace_id:
                        headers.append(("x-trace-id", message.trace_id.encode("utf-8")))

                    send_message_tasks.append(
                        self.producer.send_and_wait(
                            message.topic,
                            dumps(message.payload),
                            headers=headers,
                        )
                    )
                    message_ids.append(message.id)

                await gather(*send_message_tasks)

                await outbox_repository.batch_mark_processed(message_ids)
                await self.session.commit()

                logger.info("Successfully sent messages", count=len(message_ids))
            except Exception as exc:
                await self.session.rollback()
                raise exc
