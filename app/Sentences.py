import re
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    JSON,
    Text,
    Float,
    ForeignKey,
    insert
)
from app.Database import Base, Session


class Sentences(Base):
    __tablename__ = 'sentences'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    body = Column(Text())
    employee_id = Column(String(10))
    channel_id = Column(String(10))
    reactions = Column(JSON(none_as_null=True), default=None)
    ts = Column(Float())
    parent_ts = Column(Float())
    created_at = Column(DateTime(timezone=True), default='now()')

    @staticmethod
    def ts_exists(ts):
        query = Session.query(Sentences) \
            .filter(Sentences.ts == ts) \
            .exists()

        return Session.query(query).scalar()

    @staticmethod
    def get_user_sentences(slack_handle):
        from app.Employees import Employees
        return Session.query(Sentences) \
            .filter(Employees.slack_handle == slack_handle) \
            .filter(Employees.enabled) \
            .filter(Employees.id == Sentences.employee_id) \
            .with_entities(Sentences.body) \
            .all()

    @staticmethod
    def get_multiple_users_sentences(slack_handles):
        from app.Employees import Employees
        return Session.query(Sentences) \
            .filter(Employees.slack_handle.in_(tuple(slack_handles))) \
            .filter(Employees.enabled) \
            .filter(Employees.id == Sentences.employee_id) \
            .with_entities(Sentences.body) \
            .limit(5000) \
            .all()

    @staticmethod
    def get_user_sentences_in_channel(slack_handle, channel_name):
        from app.Employees import Employees
        from app.Channels import Channels

        return Session.query(Sentences) \
            .filter(Employees.slack_handle == slack_handle) \
            .filter(Employees.enabled) \
            .filter(Channels.name == channel_name) \
            .filter(Channels.enabled) \
            .filter(Employees.id == Sentences.employee_id) \
            .filter(Channels.id == Sentences.channel_id) \
            .with_entities(Sentences.body) \
            .all()

    @staticmethod
    def get_channel_sentences(channel_name):
        from app.Channels import Channels
        return Session.query(Sentences) \
            .filter(Channels.name == channel_name) \
            .filter(Channels.enabled) \
            .filter(Channels.id == Sentences.channel_id) \
            .with_entities(Sentences.body) \
            .all()

    @staticmethod
    def create(message, employee_id, channel_name, ts, reactions, parent_ts=None):
        new_channel = insert(Sentences) \
            .values(dict(
            body=message,
            employee_id=employee_id,
            channel_id=channel_name,
            ts=ts,
            reactions=reactions,
            parent_ts=parent_ts,
            created_at='now()',
        ))

        execute = Session.execute(new_channel)
        Session.commit()
        return execute

    @staticmethod
    def get_last_inserted_ts(channel_name):
        sentence = Session.query(Sentences) \
            .filter(Sentences.channel_id == channel_name) \
            .order_by(Sentences.ts.desc()) \
            .one()

        if sentence.ts is None:
            return 0

        return sentence.ts

    @staticmethod
    def format_all_ats(text):
        ats = re.findall(r'(<[!|@][\w]*>)', text)

        print(ats)
        for at in ats:
            is_user_mention = True
            formatted_at = at

            if '!' in at:
                is_user_mention = False

            for character in ['<', '!', '@', '>']:
                formatted_at = formatted_at.replace(character, '')

            if is_user_mention:
                from app.Employees import Employees
                formatted_string = Employees().get(formatted_at)[1]
            else:
                formatted_string = formatted_at

            text = text.replace(at, 'AT-' + formatted_string)

        return text
