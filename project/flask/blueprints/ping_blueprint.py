from flask import Blueprint


def ping():
    return "Ping"


ping_blueprint = Blueprint('ping', __name__)
ping_blueprint.add_url_rule('/ping', view_func=ping, methods=['GET', 'POST'])
