from project.common.decorators import lazy_property
from project.database.dtos.base_dto import BaseDTO


class CategoryDTO(BaseDTO):
    def __init__(self, name, weight, enabled, is_subcategory, created_at=None, updated_at=None, id=None):
        self.id = id
        self.name = name
        self.weight = weight
        self.enabled = 1 if enabled else 0
        self.is_subcategory = 1 if is_subcategory else 0
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, category_dict):
        return cls(
            name=category_dict.get('name'),
            weight=category_dict.get('weight'),
            enabled=category_dict.get('enabled'),
            is_subcategory=category_dict.get('is_subcategory'),
            created_at=category_dict.get('created_at'),
            updated_at=category_dict.get('updated_at'),
            id=category_dict.get('id'),
        )

    @lazy_property
    def frontend_object(self):
        self.enabled = self.enabled == 1
        self.is_subcategory = self.is_subcategory == 1
        return self
