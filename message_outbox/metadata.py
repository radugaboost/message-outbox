from sqlalchemy import MetaData

from message_outbox.models import Base


def get_metadata() -> MetaData:
    return Base.metadata
