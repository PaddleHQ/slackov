from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
    ForeignKey,
    func,
    insert)

from app.Database import Base, Session


class Employees(Base):
    __tablename__ = 'employees'

    id = Column(String(10), primary_key=True)
    slack_handle = Column(String(140))
    name = Column(String(140))
    enabled = Column(Boolean(), default=True)
    created_at = Column(DateTime(timezone=True), default='now()')

    @staticmethod
    def exists(slack_handle):
        from app.Sentences import Sentences
        query = Session.query(Employees, Sentences) \
            .filter(Employees.slack_handle == slack_handle) \
            .filter(Employees.enabled) \
            .filter(Employees.id == Sentences.employee_id) \
            .exists()

        return Session.query(query).scalar()

    @staticmethod
    def get_random_employee():
        from app.Sentences import Sentences
        query = Session.query(Employees, Sentences) \
            .filter(Employees.id == Sentences.employee_id) \
            .filter(Employees.enabled) \
            .order_by(func.random()) \
            .limit(1) \
            .one()

        return query.Employees.slack_handle

    @staticmethod
    def get_full_name(slack_handle):
        query = Session.query(Employees) \
            .filter(Employees.slack_handle == slack_handle) \
            .filter(Employees.enabled) \
            .limit(1) \
            .one()

        return query.name

    @staticmethod
    def toggle(slack_id, toggle):
        Session.query(Employees) \
            .filter(Employees.id == slack_id) \
            .update({'enabled': toggle})

        return Session.commit()

    @staticmethod
    def exists_by_id(id):
        query = Session.query(Employees) \
            .filter(Employees.id == id) \
            .filter(Employees.enabled) \
            .exists()

        return Session.query(query).scalar()

    @staticmethod
    def create(employee):
        new_employee = insert(Employees) \
            .values(dict(
            id=employee['id'],
            slack_handle=employee['name'],
            name=employee['profile']['real_name']
        ))

        execute = Session.execute(new_employee)
        Session.commit()
        return execute

    @staticmethod
    def get(id):
        return Session.query(Employees) \
            .filter(Employees.id == id) \
            .one()
