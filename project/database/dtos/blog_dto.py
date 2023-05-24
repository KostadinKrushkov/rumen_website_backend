from project.common.decorators import lazy_property
from project.database.dtos.base_dto import BaseDTO


class BlogDTO(BaseDTO):
    def __init__(self, title, content, image_format, image, created_at=None, updated_at=None):
        self.title = title
        self.content = content
        self.image_format = image_format
        self.image = image
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, blog_dict):
        return cls(
            title=blog_dict.get('title'),
            content=blog_dict.get('content'),
            image_format=blog_dict.get('image_format'),
            image=blog_dict.get('image'),
            created_at=blog_dict.get('created_at'),
            updated_at=blog_dict.get('updated_at')
        )

    @lazy_property
    def frontend_object(self):
        self.image = self.image.decode('utf-8')
        return super().frontend_object
