from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Questions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    its_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("quezes.id"))
    user = orm.relationship('Quezes')
    ask = sqlalchemy.Column(sqlalchemy.String, primary_key=True, autoincrement=True)
    question1 = sqlalchemy.Column(sqlalchemy.String, primary_key=True, autoincrement=True)
    question2 = sqlalchemy.Column(sqlalchemy.String, primary_key=True, autoincrement=True)
    question3 = sqlalchemy.Column(sqlalchemy.String, primary_key=True, autoincrement=True)
    question4 = sqlalchemy.Column(sqlalchemy.String, primary_key=True, autoincrement=True)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, primary_key=True, autoincrement=True)