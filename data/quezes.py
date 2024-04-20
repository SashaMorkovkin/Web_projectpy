from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Quezes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'quezes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cover = sqlalchemy.Column(sqlalchemy.String, default='images/default/cover.png')
    authorid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author = orm.relationship('User')
    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="quezes")
    mode = sqlalchemy.Column(sqlalchemy.String)
    questions = orm.relationship('Questions', back_populates='quiz')
    publicated = sqlalchemy.Column(sqlalchemy.Boolean, default=False)