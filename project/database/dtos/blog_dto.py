from project.database.dtos.base_dto import BaseDTO


class BlogDTO(BaseDTO):
    def __init__(self, title, content, image=None, created_at=None, updated_at=None):
        self.title = title
        self.content = content
        self.image = "" if not image else image
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, blog_dict):
        return cls(
            title=blog_dict.get('title'),
            content=blog_dict.get('content'),
            image=blog_dict.get('image'),
            created_at=blog_dict.get('created_at'),
            updated_at=blog_dict.get('updated_at')
        )

    def as_frontend_object(self):
        return self
