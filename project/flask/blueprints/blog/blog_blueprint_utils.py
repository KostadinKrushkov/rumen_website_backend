from project.database.database_utils import sanitize_param_for_apostrophies
from project.database.dtos.blog_dto import BlogDTO


def get_blog_dto_from_json(blog_json):
    blog_json['title'] = sanitize_param_for_apostrophies(blog_json['title'])
    blog_json['content'] = sanitize_param_for_apostrophies(blog_json['content'])

    image_format, image = blog_json['image'].split(',')
    image = image.encode('utf-8')

    return BlogDTO(
        title=blog_json['title'],
        content=blog_json['content'],
        image_format=image_format,
        image=image,
    )
