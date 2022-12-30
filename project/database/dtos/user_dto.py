from project.database.dtos.base_dto import BaseDTO
from project.database.dtos.dto_utils import sql_server_datetime_to_human_readable


class UserDTO(BaseDTO):
    def __init__(self, email, username, password, is_admin=False, is_verified=False, created_at=None, updated_at=None, id=None):
        self.email = email
        self.username = username
        self.password = password
        self.is_admin = 1 if is_admin else 0
        self.is_verified = 1 if is_verified else 0
        self.created_at = created_at
        self.updated_at = updated_at
        self.id = id

    def as_frontend_object(self):
        self.created_at = sql_server_datetime_to_human_readable(self.created_at)
        self.updated_at = sql_server_datetime_to_human_readable(self.updated_at)
        return self
