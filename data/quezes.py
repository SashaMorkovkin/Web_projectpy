from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Quezes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'quezes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    category = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('category.id'))
    questions = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relationship('User')