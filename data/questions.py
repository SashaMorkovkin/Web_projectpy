from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Questions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    quizid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("quezes.id"))
    quiz = orm.relationship('Quezes')
    title = sqlalchemy.Column(sqlalchemy.String)
    answer1 = sqlalchemy.Column(sqlalchemy.String)
    answer2 = sqlalchemy.Column(sqlalchemy.String)
    answer3 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer4 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer5 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer6 = sqlalchemy.Column(sqlalchemy.String, nullable=True)