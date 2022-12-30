from project.common.constants import SQLConstants
from project.database.dtos.category_dto import CategoryDTO
from project.database.gateways.base_gateway import BaseGateway


class CategoryGateway(BaseGateway):
    table_name = "category"
    model = CategoryDTO

    def save(self, category):
        try:
            sql = self._insert_sql_for_category(category)
            return self.db_controller.execute_get_row_count(sql)
        except Exception as e:
            if SQLConstants.DUPLICATE_KEY_ERROR in str(e):
                return None
            raise Exception(e)

    def update(self, category):
        sql = self._update_sql_for_category(category)
        return self.db_controller.execute_get_row_count(sql)

    def get_by_name(self, name):
        sql = self._get_sql_for_category_name(name)
        category_result = self.db_controller.execute_get_response(sql)
        if not category_result:
            return None
        return CategoryDTO(**category_result[0]._mapping).as_frontend_object()

    def get_by_id(self, category_id):  # TODO add testing and refactoring
        sql = self._get_sql_by_category_id(category_id)
        category_result = self.db_controller.execute_get_response(sql)
        if not category_result:
            return None
        return CategoryDTO(**category_result[0]._mapping)

    def get_all(self):
        sql = self._get_sql_for_all_categories()
        categories = self.db_controller.execute_get_response(sql)
        for category in categories:
            yield CategoryDTO(**category._mapping)

    def delete(self, category):
        sql = self._delete_sql_by_category_obj(category)
        return self.db_controller.execute_get_row_count(sql)

    def delete_by_name(self, name):
        sql = self._delete_sql_by_category_name(name)
        return self.db_controller.execute_get_row_count(sql)

    def _insert_sql_for_category(self, category):
        return f"""
INSERT INTO {self.table_name} (name, weight, enabled, is_subcategory, created_at, updated_at)
VALUES ('{category.name}', {category.weight}, {category.enabled}, {category.is_subcategory}, GETDATE(), GETDATE());"""

    def _update_sql_for_category(self, category):
        return f"""
UPDATE {self.table_name} 
SET weight = {category.weight}, enabled = {category.enabled}, is_subcategory = {category.is_subcategory}, updated_at = GETDATE()
WHERE name = '{category.name}';
"""

    def _get_sql_for_all_categories(self):
        return f"""SELECT id, name, weight, enabled, is_subcategory, created_at, updated_at FROM {self.table_name}"""

    def _get_sql_for_category_name(self, category_name):
        return f"""SELECT id, name, weight, enabled, is_subcategory, created_at, updated_at
FROM {self.table_name} WHERE name = '{category_name}'"""

    def _get_sql_by_category_id(self, category_id):
        return f"""SELECT id, name, weight, enabled, is_subcategory, created_at, updated_at
        FROM {self.table_name} WHERE id = {category_id}"""

    def _delete_sql_by_category_name(self, category_name):
        return f"""DELETE FROM {self.table_name} WHERE name = '{category_name}'"""

    def _delete_sql_by_category_obj(self, category):
        return self._delete_sql_by_category_name(category.name)
