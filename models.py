import datetime

from pony.orm import Database, Required, Optional, PrimaryKey

database = Database()


class Article(database.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    markdown = Required(str)
    html = Required(str)
    upload_date = Required(datetime.date)
    last_edit_date = Optional(datetime.date)


database.bind(provider="sqlite", filename="articles.db", create_db=True)
database.generate_mapping(create_tables=True)
