import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    folowed = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='Не важно')
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    avatar = sqlalchemy.Column(sqlalchemy.String, default='images/default/avatar.jpg')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.String, default='False')
    quezes = orm.relationship("Quezes", back_populates='author')
    vkid = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)