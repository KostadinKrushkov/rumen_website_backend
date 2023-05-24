from functools import wraps

from sqlalchemy.sql.expression import text


def sanitize_sql(func):

    @wraps(func)
    def wrapper(sql, *args, **kwargs):
        sanitized_sql = text(sql)
        return func(sanitized_sql, *args, **kwargs)
    return wrapper


def sanitize_param_for_apostrophies(param):
    return param.replace("'", "''")
