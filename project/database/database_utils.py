from functools import wraps

from sqlalchemy.sql.expression import text


def sanitize_sql(func):

    @wraps(func)
    def wrapper(sql):
        sanitized_sql = text(sql)
        return func(sanitized_sql)
    return wrapper
