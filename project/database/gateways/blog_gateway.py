from copy import copy
from functools import lru_cache

from project.common.constants import SQLConstants
from project.database.dtos.blog_dto import BlogDTO
from project.database.gateways.base_gateway import BaseGateway
from project.flask.blueprints.blog.blog_exceptions import DuplicateBlogTitle
from project.flask.blueprints.picture.picture_blueprint_utils import compress_image


class BlogGateway(BaseGateway):
    table_name = "blog"
    dto_class = BlogDTO

    def clear_cache(self):
        self.get_all.cache_clear()
        self.get_all_compressed.cache_clear()

    def save(self, blog):
        super(BlogGateway, self).save(blog)

        sql = self._insert_sql_for_blog()
        blog_params = {
            'title': blog.title,
            'content': blog.content,
            'image_format': blog.image_format,
            'image': blog.image,
        }

        try:
            return self.db_controller.execute_get_row_count(sql, **blog_params) == 1
        except Exception as e:
            if SQLConstants.DUPLICATE_KEY_ERROR in str(e):
                raise DuplicateBlogTitle(e)
            raise e

    def update(self, blog):
        super(BlogGateway, self).update(blog)

        sql = self._update_sql_for_blog()
        blog_params = {
            'title': blog.title,
            'content': blog.content,
            'image_format': blog.image_format,
            'image': blog.image,
        }

        return self.db_controller.execute_get_row_count(sql, **blog_params) == 1

    def get_by_title(self, title):
        sql = self._get_sql_for_blog_title(title)
        results = self.db_controller.execute_get_response(sql)
        return self.dto_class(**results[0]._mapping) if results else None

    @lru_cache(maxsize=None)
    def get_all(self):
        sql = self._get_sql_for_all_blogs()
        blog_results = []
        for blog in self.db_controller.execute_get_response(sql):
            blog_results.append(self.dto_class(**blog))
        return blog_results

    @lru_cache(maxsize=None)
    def get_all_compressed(self):
        blog_results = []

        for blog in self.get_all():
            copy_blog = copy(blog)
            copy_blog.image = compress_image(copy_blog.image_format, copy_blog.image)
            blog_results.append(copy_blog)
        return blog_results

    def delete_by_title(self, title):
        super(BlogGateway, self).delete(title)

        sql = self._delete_sql_by_blog_title(title)
        return self.db_controller.execute_get_row_count(sql) == 1

    @classmethod
    def _insert_sql_for_blog(cls):
        return f"""
INSERT INTO dbo.{cls.table_name} (title, content, image_format, image, created_at, updated_at)
VALUES (:title, :content, :image_format, :image, GETDATE(), GETDATE());"""

    @classmethod
    def _update_sql_for_blog(cls):
        return f"""
UPDATE dbo.{cls.table_name} 
SET content = :content, image_format = :image_format, image = :image, updated_at = GETDATE()
WHERE title = :title ;
"""

    def _get_sql_for_all_blogs(self):
        return f"""
SELECT title, content, image_format, image, created_at, updated_at FROM dbo.{self.table_name} 
ORDER BY created_at ASC"""

    def _get_sql_for_blog_title(self, blog_title):
        return f"""
SELECT title, content, image_format, image, created_at, updated_at FROM dbo.{self.table_name}  
WHERE title = '{blog_title}'
"""

    def _delete_sql_by_blog_title(self, blog_title):
        return f"""DELETE FROM dbo.{self.table_name} WHERE title = '{blog_title}'"""
