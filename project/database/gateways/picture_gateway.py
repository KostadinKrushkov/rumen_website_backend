from project.common.constants import SQLConstants
from project.database.dtos.picture_dto import PictureDTO
from project.database.gateways.base_gateway import BaseGateway


class PictureGateway(BaseGateway):
    table_name = "picture"
    model = PictureDTO

    def save(self, picture):
        try:
            sql = self._insert_sql_for_picture(picture)
            return self.db_controller.execute_get_row_count(sql)
        except Exception as e:
            if SQLConstants.DUPLICATE_KEY_ERROR in str(e):
                return None
            raise Exception(e)

    def update(self, picture):
        sql = self._update_sql_for_picture(picture)
        return self.db_controller.execute_get_row_count(sql)

    def get_by_title(self, title):
        sql = self._get_sql_for_picture_title(title)
        found_picture = self.db_controller.execute_get_response(sql)
        picture_dto = PictureDTO.from_row(found_picture)
        return picture_dto.as_frontend_object() if picture_dto is not None else None

    def get_all(self):
        sql = self._get_sql_for_all_pictures()
        picture_results = self.db_controller.execute_get_response(sql)
        for picture in picture_results:
            yield PictureDTO(**picture._mapping)

    def delete(self, picture):
        sql = self._delete_sql_by_picture_obj(picture)
        return self.db_controller.execute_get_row_count(sql)

    def delete_by_title(self, title):
        sql = self._delete_sql_by_picture_title(title)
        return self.db_controller.execute_get_row_count(sql)

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

    def _get_sql_for_all_pictures(self):
        return f"""SELECT title, description, category_id, image, created_at, updated_at FROM {self.table_name}"""

    def _get_sql_for_picture_title(self, picture_title):
        return f"""
SELECT title, description, category_id, image, created_at, updated_at 
FROM {self.table_name} WHERE title = '{picture_title}'"""

    def _delete_sql_by_picture_id(self, id):
        return f"""DELETE FROM {self.table_name} WHERE id = {id}"""

    def _delete_sql_by_picture_title(self, picture_title):
        return f"""DELETE FROM {self.table_name} WHERE title = '{picture_title}'"""

    def _delete_sql_by_picture_obj(self, picture):
        return self._delete_sql_by_picture_title(picture.title)
