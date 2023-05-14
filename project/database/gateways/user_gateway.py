from project.common.constants import SQLConstants
from project.database.dtos.user_dto import UserDTO
from project.database.gateways.base_gateway import BaseGateway


class UserGateway(BaseGateway):
    table_name = "users"
    dto_class = UserDTO

    def save(self, user):
        try:
            sql = self._insert_sql_for_user(user)
            return self.db_controller.execute_get_row_count(sql) == 1
        except Exception as e:
            if SQLConstants.DUPLICATE_KEY_ERROR in str(e):
                return None
            raise Exception(e)

    def update(self, user):
        sql = self._update_sql_for_user(user)
        return self.db_controller.execute_get_row_count(sql) == 1

    def get_by_username(self, username):
        if not username:
            return None

        sql = self._get_sql_for_username(username)
        result = self.db_controller.execute_get_response(sql)

        if not result:
            return None
        return self.dto_class(**dict(result[0]))

    def get_by_id(self, user_id):
        if not user_id:
            return None

        sql = self._get_sql_for_id(user_id)
        result = self.db_controller.execute_get_response(sql)

        if not result:
            return None
        return self.dto_class(**dict(result[0]))

    def get_all(self):
        sql = self._get_sql_for_all_users()
        user_results = self.db_controller.execute_get_response(sql)
        for user in user_results:
            yield self.dto_class(**dict(user))

    def delete(self, user):
        return self.delete_by_username(user.username)

    def delete_by_username(self, email):
        sql = self._delete_sql_by_username(email)
        return self.db_controller.execute_get_row_count(sql) == 1

    def delete_by_email(self, email):
        sql = self._delete_sql_by_email(email)
        return self.db_controller.execute_get_row_count(sql) == 1

    def _insert_sql_for_user(self, user):
        return f"""
INSERT INTO {self.table_name} (email, username, password, is_admin, is_verified, created_at, updated_at)
VALUES ('{user.email}', '{user.username}', '{user.password}', {user.is_admin}, {user.is_verified}, GETDATE(), GETDATE());"""

    def _update_sql_for_user(self, user):
        return f"""
UPDATE {self.table_name} 
SET password = '{user.password}', is_admin = {user.is_admin}, is_verified = {user.is_verified}, updated_at = GETDATE()
WHERE username = '{user.username}';
"""

    def _get_sql_for_all_users(self):
        return f"""SELECT email, username, password, is_admin, is_verified, created_at, updated_at FROM {self.table_name}"""

    def _get_sql_for_username(self, username):
        return f"""
SELECT id, email, username, password, is_admin, is_verified, created_at, updated_at 
FROM {self.table_name} WHERE username = '{username}'"""

    def _get_sql_for_username_or_email(self, username, email):
        return f"""
SELECT id, email, username, password, is_admin, is_verified, created_at, updated_at 
FROM {self.table_name} WHERE username = '{username}' or email = '{email}'"""

    def _get_sql_for_id(self, user_id):
        return f"""
SELECT id, email, username, password, is_admin, is_verified, created_at, updated_at 
FROM {self.table_name} WHERE id = {user_id}"""

    def _delete_sql_by_email(self, email):
        return f"""DELETE FROM {self.table_name} WHERE email = '{email}'"""

    def _delete_sql_by_username(self, username):
        return f"""DELETE FROM {self.table_name} WHERE username = '{username}'"""
