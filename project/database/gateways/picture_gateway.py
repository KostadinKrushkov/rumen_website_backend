from functools import lru_cache

from project.common.constants import SQLConstants
from project.database.dtos.picture_dto import PictureDTO
from project.database.gateways.base_gateway import BaseGateway
from project.flask.blueprints.picture.picture_exceptions import DuplicatePictureTitle


class PictureGateway(BaseGateway):
    table_name = "picture"
    model = PictureDTO

    def clear_cache(self):
        self.get_all.cache_clear()
        self.get_distinct_picture_years.cache_clear()

    def save(self, picture):
        super(PictureGateway, self).save(picture)

        try:
            sql = self._insert_sql_for_picture(picture)
            return self.db_controller.execute_get_row_count(sql) == 1
        except Exception as e:
            if SQLConstants.DUPLICATE_KEY_ERROR in str(e):
                raise DuplicatePictureTitle()
            raise Exception(e)

    def update(self, picture):
        super(PictureGateway, self).update(picture)

        sql = self._update_sql_for_picture(picture)
        return self.db_controller.execute_get_row_count(sql) == 1

    @lru_cache()
    def get_distinct_picture_years(self):
        sql = self._get_sql_distinct_years_from_pictures()
        return self.db_controller.execute_get_response(sql)

    def get_by_title(self, title):
        sql = self._get_sql_for_picture_title(title)
        found_picture = self.db_controller.execute_get_response(sql)
        picture_dto = PictureDTO.from_row(found_picture)
        return picture_dto.as_frontend_object() if picture_dto is not None else None

    @lru_cache(maxsize=None)
    def get_all(self):
        sql = self._get_sql_for_all_pictures()
        picture_results = []
        for picture in self.db_controller.execute_get_response(sql):
            picture_results.append(PictureDTO(**picture._mapping))
        return picture_results

    # deprecated in favor of caching all and filtering in code
    def get_pictures(self, categories, years, limit=None, cursor_picture_title=None):
        conditions = ['c.enabled = 1']

        if categories:
            category_names = ','.join(f"'{category_name}'" for category_name in categories)
            conditions.append(f'c.name in ({category_names})')
        if years:
            conditions.append(f'YEAR(p.created_at) IN ({",".join(years)})')
        if cursor_picture_title:
            select_cursor_picture_sql = f"(SELECT id FROM {self.table_name} WHERE title = '{cursor_picture_title}')"
            conditions.append(f'p.created_at < (SELECT created_at FROM {self.table_name} WHERE id = {select_cursor_picture_sql})')

        limit_clause = f'TOP {limit}' if limit else ''
        where_clause = f'WHERE {conditions[0]} '
        for condition in conditions[1:]:
            where_clause += f' AND {condition}'

        sql = f"""
SELECT {limit_clause} p.title, p.description, p.category_id, c.name as category, p.image, p.created_at, p.updated_at FROM {self.table_name} p
JOIN category c on c.id = p.category_id
{where_clause}
ORDER BY p.created_at DESC
"""

        for picture in self.db_controller.execute_get_response(sql):
            yield PictureDTO(**picture._mapping)

    def delete(self, picture):
        super(PictureGateway, self).delete(picture)

        sql = self._delete_sql_by_picture_obj(picture)
        return self.db_controller.execute_get_row_count(sql) == 1

    def delete_by_title(self, title):
        self.clear_cache()

        sql = self._delete_sql_by_picture_title(title)
        return self.db_controller.execute_get_row_count(sql) == 1

    def _insert_sql_for_picture(self, picture):
        return f"""
INSERT INTO picture (title, description, category_id, image, created_at, updated_at)
values ('{picture.title}', '{picture.description}', {picture.category_id}, '{picture.image}', GETDATE(), GETDATE());
"""

    def _update_sql_for_picture(self, picture):
        return f"""
UPDATE {self.table_name} 
SET description = '{picture.description}', category_id = '{picture.category_id}', image = '{picture.image}', updated_at = GETDATE() where title = '{picture.title}'
"""

    def _get_sql_distinct_years_from_pictures(self):
        return f"""SELECT distinct(year(created_at)) as year from {self.table_name}"""

    def _get_sql_for_all_pictures(self):
        return f"""
SELECT p.title, p.description, p.category_id, c.name as category, p.image, p.created_at, p.updated_at, p.id FROM {self.table_name} p
JOIN category c ON c.id = p.category_id"""

    def _get_sql_for_picture_title(self, picture_title):
        return f"""
SELECT p.title, p.description, p.category_id, c.name as category, p.image, p.created_at, p.updated_at 
FROM {self.table_name} p
JOIN category c ON c.id = p.category_id
WHERE title = '{picture_title}'
"""

    def _delete_sql_by_picture_id(self, id):
        return f"""DELETE FROM {self.table_name} WHERE id = {id}"""

    def _delete_sql_by_picture_title(self, picture_title):
        return f"""DELETE FROM {self.table_name} WHERE title = '{picture_title}'"""

    def _delete_sql_by_picture_obj(self, picture):
        return self._delete_sql_by_picture_title(picture.title)
