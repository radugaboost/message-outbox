from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class MessageBaseSchema(BaseSchema):
    topic: str
    trace_id: str | None = None
    event_type: str
    payload: str


class MessageSchema(MessageBaseSchema):
    id: UUID


class KafkaMessageValueSchema(BaseSchema):
    event_type: str
    payload: str
