from data.db_session import create_session, global_init
from data.category import Category


def get_category():
    global_init('db/blogs.db')
    sess = create_session()
    for title in sess.query(Category).all():
        print(title.id)


get_category()