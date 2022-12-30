from project.common.constants import ResponseConstants
from project.database.dtos.picture_dto import PictureDTO
from project.flask.blueprints.category.category_blueprint import get_category_by_name
from project.flask.blueprints.category.category_exceptions import CategoryNotFound


def get_picture_dto_from_json(picture_json):
    category_name = picture_json['category'] if picture_json['category'] else None
    category = get_category_by_name(category_name)
    if not category:
        raise CategoryNotFound(ResponseConstants.UPDATE_CATEGORY_NOT_FOUND)

    return PictureDTO(title=picture_json['title'],
                      description=picture_json['description'],
                      category_id=int(category.id),
                      image=picture_json['image'])
