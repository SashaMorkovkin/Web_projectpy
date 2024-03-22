from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Questions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    its_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("quezes.id"))
    user = orm.relationship('Quezes')