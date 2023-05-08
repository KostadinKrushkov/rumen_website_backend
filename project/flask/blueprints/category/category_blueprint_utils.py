from project.database.database_utils import sanitize_param_for_apostrophies
from project.database.dtos.category_dto import CategoryDTO


def get_category_dto_from_json(category_json):
    category_json['name'] = sanitize_param_for_apostrophies(category_json['name'])

    return CategoryDTO(name=category_json['name'],
                       weight=category_json['weight'],
                       enabled=category_json['enabled'],
                       is_subcategory=category_json['is_subcategory'])
