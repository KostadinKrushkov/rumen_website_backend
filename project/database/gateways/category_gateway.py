from functools import lru_cache

from project.common.constants import SQLConstants
from project.database.dtos.category_dto import CategoryDTO
from project.database.gateways.base_gateway import BaseGateway
from project.flask.blueprints.category.category_exceptions import DuplicateCategoryName


class CategoryGateway(BaseGateway):
    table_name = "category"
    dto_class = CategoryDTO

    def clear_cache(self):
        self.get_all.cache_clear()

    def save(self, category):
        super(CategoryGateway, self).save(category)
        try:
            sql = self._insert_sql_for_category(category)
            self.clear_cache()
            return self.db_controller.execute_get_row_count(sql) == 1
        except Exception as e:
            if SQLConstants.DUPLICATE_KEY_ERROR in str(e):  # it's already saved
                raise DuplicateCategoryName()
            raise Exception(e)

    def update(self, category):
        super(CategoryGateway, self).update(category)

        sql = self._update_sql_for_category(category)
        return self.db_controller.execute_get_row_count(sql) == 1

    def get_by_name(self, name):
        sql = self._get_sql_for_category_name(name)
        category_result = self.db_controller.execute_get_response(sql)
        return self.dto_class(**category_result[0]._mapping) if category_result else None

    def get_by_id(self, category_id):
        sql = self._get_sql_by_category_id(category_id)
        category_result = self.db_controller.execute_get_response(sql)
        return self.dto_class(**category_result[0]._mapping) if category_result else None

    @lru_cache(maxsize=None)
    def get_all(self):
        sql = self._get_sql_for_all_categories()
        return self._get_categories(sql)

    def _get_categories(self, sql):
        categories = []
        for category in self.db_controller.execute_get_response(sql):
            categories.append(self.dto_class(**category._mapping))
        return categories

    def delete(self, category):
        super(CategoryGateway, self).delete(category)

        sql = self._delete_sql_by_category_obj(category)
        return self.db_controller.execute_get_row_count(sql) == 1

    def delete_by_name(self, name):
        self.clear_cache()

        sql = self._delete_sql_by_category_name(name)
        return self.db_controller.execute_get_row_count(sql) == 1

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
        return f"""
SELECT id, name, weight, enabled, is_subcategory, created_at, updated_at FROM {self.table_name} 
ORDER BY weight DESC"""

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
