from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageBaseSchema(BaseModel):
    topic: str
    trace_id: str | None = None
    payload: dict[str, Any]

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class MessageSchema(MessageBaseSchema):
    id: UUID
