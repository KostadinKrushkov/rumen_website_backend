from project.database.database_controller import DatabaseController
from project.database.dtos.blog_dto import BlogDTO
from project.database.gateways.blog_gateway import BlogGateway


class TestDatabaseController:
    blog_gateway = BlogGateway()
    get_blogs_query = "SELECT title, content, image, created_at, updated_at FROM blog"

    def setup_test_data(self):
        self.blog1 = BlogDTO("new title", "new content")
        self.blog2 = BlogDTO("new title2", "new content2")

        self.blog_gateway.save(self.blog1)
        self.blog_gateway.save(self.blog2)

    def test_execute_query_and_get_response(self, client):
        result = DatabaseController.execute_get_response(self.get_blogs_query)
        assert result == []

        self.setup_test_data()

        result = DatabaseController.execute_get_response(self.get_blogs_query)
        queried_blog_dto = BlogDTO(**result[0]._mapping)
        assert queried_blog_dto.title == self.blog1.title
        assert queried_blog_dto.content == self.blog1.content

    def test_execute_query_and_get_row_count(self, client):
        self.setup_test_data()
        self.blog1.image = "some image"
        update_blogs_query = self.blog_gateway._update_sql_for_blog(self.blog1)
        result = DatabaseController.execute_get_row_count(update_blogs_query)
        assert result == 1

    def test_execute_query_no_response(self, client):
        insert_blog_query = "INSERT INTO {table_name} (title, content, image, created_at, updated_at)" \
                            "VALUES ('{title}', '{content}', '{image}', GETDATE(), GETDATE());".format(
            table_name='blog', title="newest title", content='newest content', image='newest image')
        assert len(list(self.blog_gateway.get_all())) == 0

        assert None == DatabaseController.execute(insert_blog_query)
        assert len(list(self.blog_gateway.get_all())) == 1
