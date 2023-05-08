from project.common.constants import SQLConstants
from project.database.dtos.blog_dto import BlogDTO
from project.database.gateways.base_gateway import BaseGateway
from project.flask.blueprints.blog.blog_exceptions import DuplicateBlogTitle


class BlogGateway(BaseGateway):
    table_name = "blog"
    model = BlogDTO

    def save(self, blog):
        sql = self._insert_sql_for_blog(blog)
        try:
            return self.db_controller.execute_get_row_count(sql) == 1
        except Exception as e:
            if SQLConstants.DUPLICATE_KEY_ERROR in str(e):
                raise DuplicateBlogTitle(e)
            raise e

    def update(self, blog):
        sql = self._update_sql_for_blog(blog)
        return self.db_controller.execute_get_row_count(sql) == 1

    def get_by_title(self, title):
        sql = self._get_sql_for_blog_title(title)
        results = self.db_controller.execute_get_response(sql)
        return BlogDTO(**results[0]._mapping) if results else None

    def get_all(self):
        sql = self._get_sql_for_all_blogs()
        blog_results = self.db_controller.execute_get_response(sql)
        for blog in blog_results:
            yield BlogDTO(**blog)

    def delete_by_title(self, title):
        sql = self._delete_sql_by_blog_title(title)
        return self.db_controller.execute_get_row_count(sql) == 1

    def _insert_sql_for_blog(self, blog):
        return f"""
INSERT INTO dbo.{self.table_name} (title, content, image, created_at, updated_at)
VALUES ('{blog.title}', '{blog.content}', '{blog.image}', GETDATE(), GETDATE());"""

    def _update_sql_for_blog(self, blog):
        return f"""
UPDATE dbo.{self.table_name} 
SET content = '{blog.content}', image = '{blog.image}', updated_at = GETDATE()
WHERE title = '{blog.title}';
"""

    def _get_sql_for_all_blogs(self):
        return f"""SELECT title, content, image, created_at, updated_at FROM dbo.{self.table_name} ORDER BY created_at"""

    def _get_sql_for_blog_title(self, blog_title):
        return f"""
SELECT title, content, image, created_at, updated_at FROM dbo.{self.table_name}  
WHERE title = '{blog_title}'
"""

    def _delete_sql_by_blog_title(self, blog_title):
        return f"""DELETE FROM dbo.{self.table_name} WHERE title = '{blog_title}'"""
