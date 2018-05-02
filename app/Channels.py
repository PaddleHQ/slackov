from sqlalchemy import (
    Boolean,
    Column,
    String,
    insert,
    Integer
)
from app.Database import Base, Session


class Channels(Base):
    __tablename__ = "channels"

    id = Column(String(10), primary_key=True)
    name = Column(String(22))
    enabled = Column(Boolean(), default=True)
    channel_created = Column(Integer())

    @staticmethod
    def exists(name):
        from app.Sentences import Sentences
        query = Session.query(Channels, Sentences) \
            .filter(Channels.name == name) \
            .filter(Channels.id == Sentences.channel_id) \
            .exists()

        return Session.query(query).scalar()

    @staticmethod
    def get_all_channels():
        return Session.query(Channels) \
            .filter(Channels.enabled == True) \
            .all()

    @staticmethod
    def exists_by_id(channel_id):
        from app.Sentences import Sentences
        query = Session.query(Sentences) \
            .filter(Channels.id == channel_id) \
            .exists()

        return Session.query(query).scalar()

    @staticmethod
    def create(channel):
        new_channel = insert(Channels) \
            .values(dict(
            id=channel['id'],
            name=channel['name'],
            channel_created=channel['created']
        ))

        execute = Session.execute(new_channel)
        Session.commit()
        return execute
