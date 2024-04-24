import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


follow = sqlalchemy.Table(
    'follow',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('followed', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id'), primary_key=True),
    sqlalchemy.Column('follower', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id'), primary_key=True)
)



class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    following = orm.relationship(
        'User', lambda: follow,
        primaryjoin=lambda: User.id == follow.c.followed,
        secondaryjoin=lambda: User.id == follow.c.follower,
        backref='followers'
    )
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='Не важно')
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    vk_photo = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    avatar = sqlalchemy.Column(sqlalchemy.String)
    vk_id = sqlalchemy.Column(sqlalchemy.Integer, default=None)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.String, default='False')
    quezes = orm.relationship("Quezes", back_populates='author')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)