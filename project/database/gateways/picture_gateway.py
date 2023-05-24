from copy import copy
from functools import lru_cache

from project.common.constants import SQLConstants
from project.database.dtos.picture_dto import PictureDTO
from project.database.gateways.base_gateway import BaseGateway
from project.flask.blueprints.picture.picture_blueprint_utils import compress_image
from project.flask.blueprints.picture.picture_exceptions import DuplicatePictureTitle


class PictureGateway(BaseGateway):
    table_name = "picture"
    dto_class = PictureDTO

    def clear_cache(self):
        self.get_all.cache_clear()
        self.get_all_compressed.cache_clear()
        self.get_distinct_picture_years.cache_clear()

    def save(self, picture):
        super(PictureGateway, self).save(picture)

        try:
            sql = self._insert_sql_for_picture()
            picture_data = {
                'title': picture.title,
                'description': picture.description,
                'category_id': picture.category_id,
                'image_format': picture.image_format,
                'image': picture.image,
            }
            return self.db_controller.execute_get_row_count(sql, **picture_data) == 1
        except Exception as e:
            if SQLConstants.DUPLICATE_KEY_ERROR in str(e):
                raise DuplicatePictureTitle()
            raise Exception(e)

    def update(self, picture):
        super(PictureGateway, self).update(picture)

        sql = self._update_sql_for_picture()
        picture_data = {
            'title': picture.title,
            'description': picture.description,
            'category_id': picture.category_id,
            'image_format': picture.image_format,
            'image': picture.image,
        }
        return self.db_controller.execute_get_row_count(sql, **picture_data) == 1

    @lru_cache()
    def get_distinct_picture_years(self):
        sql = self._get_sql_distinct_years_from_pictures()
        return self.db_controller.execute_get_response(sql)

    def get_by_title(self, title):
        sql = self._get_sql_for_picture_title(title)
        found_picture = self.db_controller.execute_get_response(sql)
        picture_dto = self.dto_class.from_row(found_picture)
        return picture_dto.frontend_object if picture_dto is not None else None

    @lru_cache(maxsize=None)
    def get_all(self):
        sql = self._get_sql_for_all_pictures()
        picture_results = []
        for picture in self.db_controller.execute_get_response(sql):
            picture_results.append(self.dto_class(**picture._mapping))
        return picture_results

    @lru_cache(maxsize=None)
    def get_all_compressed(self):
        picture_results = []
        for picture in self.get_all():
            copy_picture = copy(picture)
            copy_picture.image = compress_image(copy_picture.image_format, copy_picture.image)
            picture_results.append(copy_picture)
        return picture_results

    def delete(self, picture):
        super(PictureGateway, self).delete(picture)

        sql = self._delete_sql_by_picture_obj(picture)
        return self.db_controller.execute_get_row_count(sql) == 1

    def delete_by_title(self, title):
        self.clear_cache()

        sql = self._delete_sql_by_picture_title(title)
        return self.db_controller.execute_get_row_count(sql) == 1

    @classmethod
    def _insert_sql_for_picture(cls):
        return f"""
INSERT INTO {cls.table_name} (title, description, category_id, image_format, image, created_at, updated_at)
values (:title, :description, :category_id, :image_format, :image, GETDATE(), GETDATE());
"""

    @classmethod
    def _update_sql_for_picture(cls):
        return f"""
UPDATE {cls.table_name} 
SET title = :title,
    description = :description,
    category_id = :category_id,
    image_format = :image_format,
    image = :image,
    updated_at = GETDATE()
WHERE title = :title
"""

    def _get_sql_distinct_years_from_pictures(self):
        return f"""SELECT distinct(year(created_at)) as year from {self.table_name}"""

    def _get_sql_for_all_pictures(self):
        return f"""
SELECT p.title, p.description, p.category_id, c.name as category, p.image_format, p.image, p.created_at, p.updated_at, p.id FROM {self.table_name} p
JOIN category c ON c.id = p.category_id
ORDER BY p.created_at ASC
"""

    def _get_sql_for_picture_title(self, picture_title):
        return f"""
SELECT p.title, p.description, p.category_id, c.name as category, p.image_format, p.image, p.created_at, p.updated_at 
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
