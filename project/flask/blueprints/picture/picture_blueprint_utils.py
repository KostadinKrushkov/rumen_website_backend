import base64
import io
from PIL import Image

from project.common.constants import ResponseConstants
from project.database.database_utils import sanitize_param_for_apostrophies
from project.database.dtos.picture_dto import PictureDTO
from project.flask.blueprints.category.category_blueprint import get_category_by_name
from project.flask.blueprints.category.category_exceptions import CategoryNotFound


def get_picture_dto_from_json(picture_json):
    picture_json['title'] = sanitize_param_for_apostrophies(picture_json['title'])
    picture_json['description'] = sanitize_param_for_apostrophies(picture_json['description'])

    image_format, image = picture_json['image'].split(',')
    image = image.encode('utf-8')

    category_name = picture_json['category'] if picture_json.get('category') else None
    category = get_category_by_name(category_name)
    if not category:
        raise CategoryNotFound(ResponseConstants.UPDATE_CATEGORY_NOT_FOUND)

    return PictureDTO(
        title=picture_json['title'],
        description=picture_json['description'],
        category_id=int(category['id']),
        category=category['name'],
        image_format=image_format,
        image=image
    )


def parse_image_format(ui_format):
    return ui_format.split('/')[1].split(';')[0].upper()


def compress_image(image_format, image, quality=80, max_size=1024):
    image_bytes = io.BytesIO(base64.b64decode(image))
    image_format = parse_image_format(image_format)

    pil_image = Image.open(image_bytes)

    width_to_height = pil_image.width / pil_image.height

    final_height = final_width = max_size
    if width_to_height > 1:
        final_width = max_size * width_to_height
    else:
        final_height = max_size * (1 / width_to_height)

    pil_image = pil_image.resize((int(final_width), int(final_height)), Image.ANTIALIAS)

    output_buffer = io.BytesIO()
    pil_image.save(output_buffer, format=image_format, quality=quality)
    compressed_image = output_buffer.getvalue()
    return base64.b64encode(compressed_image)
