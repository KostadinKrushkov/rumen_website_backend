from project.database.database_controller import DatabaseController
from project.database.dtos.blog_dto import BlogDTO
from project.database.gateways.blog_gateway import BlogGateway
from tests.integration_tests.blueprints.test_stubs import image_base64, image_format


class TestDatabaseController:
    blog_gateway = BlogGateway()
    get_blogs_query = blog_gateway._get_sql_for_all_blogs()

    image = image_base64.encode('utf-8')
    image_format = image_format

    def setup_test_data(self):
        self.blog1 = BlogDTO(title="new title", content="new content",
                             image=self.image, image_format=self.image_format)
        self.blog2 = BlogDTO(title="new title2", content="new content2",
                             image=self.image, image_format=self.image_format)

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
        self.blog1.content = "some image"
        update_blogs_query = self.blog_gateway._update_sql_for_blog()
        blog_params = {
            'title': self.blog1.title,
            'content': self.blog1.content,
            'image_format': self.blog1.image_format,
            'image': self.blog1.image,
        }

        assert DatabaseController.execute_get_row_count(update_blogs_query, **blog_params) == 1

    def test_execute_query_no_response(self, client):
        self.setup_test_data()
        self.blog2.title = 'the newest blog'

        assert len(list(self.blog_gateway.get_all())) == 2

        assert self.blog_gateway.save(self.blog2)

        self.blog_gateway.clear_cache()
        assert len(list(self.blog_gateway.get_all())) == 3
