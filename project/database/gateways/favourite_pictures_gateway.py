from copy import copy
from functools import lru_cache

from project.database.dtos.picture_dto import PictureDTO
from project.database.gateways.base_gateway import BaseGateway
from project.flask.blueprints.picture.picture_blueprint_utils import compress_image


class FavouritePicturesGateway(BaseGateway):
    table_name = "favourite_pictures"
    dto_class = PictureDTO

    def clear_cache(self):
        self.get_all.cache_clear()
        self.get_all_compressed.cache_clear()

    def overwrite_data(self, picture_titles):
        self.clear_cache()
        sql = self._overwrite_pictures_sql(picture_titles)
        return self.db_controller.execute_get_row_count(sql) != 0

    @lru_cache(maxsize=None)
    def get_all(self):
        sql = self._get_sql_for_all_pictures()

        fav_pictures = []
        for picture in self.db_controller.execute_get_response(sql):
            fav_pictures.append(self.dto_class(**picture._mapping))

        return fav_pictures

    @lru_cache(maxsize=None)
    def get_all_compressed(self):
        fav_pictures = []

        for picture in self.get_all():
            copy_picture = copy(picture)
            copy_picture.image = compress_image(copy_picture.image_format, copy_picture.image)
            fav_pictures.append(copy_picture)

        return fav_pictures

    def _overwrite_pictures_sql(self, picture_titles):
        picture_titles_string = ', '.join(f"'{title}'" for title in picture_titles)

        select_pictures_sql = f"""
SELECT p.id, GETDATE(), GETDATE() FROM picture p
WHERE p.title in ({picture_titles_string})
"""

        return f"""
DELETE FROM {self.table_name};
INSERT INTO {self.table_name} (picture_id, created_at, updated_at)
{select_pictures_sql};
"""

    def _get_sql_for_all_pictures(self):
        return f"""
SELECT p.title, p.description, p.category_id, c.name as category, p.image_format, p.image, f.created_at, f.updated_at, p.id FROM {self.table_name} f
JOIN picture p ON p.id = f.picture_id
JOIN category c ON c.id = p.category_id
"""
