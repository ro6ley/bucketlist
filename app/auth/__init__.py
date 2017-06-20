from flask import Blueprint

# The authentication blueprint
auth_blueprint = Blueprint("auth", __name__)

from . import views
