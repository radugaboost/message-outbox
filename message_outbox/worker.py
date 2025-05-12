from asyncio import gather, sleep

from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from structlog import get_logger

from message_outbox.repositories import MessageOutboxRepository
from message_outbox.schemas import KafkaMessageValueSchema

logger = get_logger(__name__)


class MessageOutboxWorker:
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        producer: AIOKafkaProducer,
        timeout: int = 2,
    ) -> None:
        self.session_maker = session_maker
        self.kafka_producer = producer
        self.timeout = timeout

    async def process_events(self) -> None:
        logger.info("Starting event outbox worker")

        async with self.kafka_producer as producer:
            while True:
                async with self.session_maker() as session:
                    repository = MessageOutboxRepository(session)

                    messages = await repository.get()
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
                                producer.send_and_wait(
                                    topic=message.topic,
                                    value=KafkaMessageValueSchema(
                                        event_type=message.event_type, payload=message.payload
                                    )
                                    .model_dump_json()
                                    .encode("utf-8"),
                                    headers=headers,
                                )
                            )
                            message_ids.append(message.id)

                        await gather(*send_message_tasks)

                        await repository.batch_mark_processed(message_ids)
                        await session.commit()

                        logger.info("Successfully sent messages", count=len(message_ids))
                    except Exception as exc:
                        await session.rollback()
                        raise exc
