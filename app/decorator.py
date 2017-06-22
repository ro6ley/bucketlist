from functools import wraps
from flask import jsonify, request, abort, make_response

from app.models import BucketList, Item, User


def check_auth(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        # Check for the authentication token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            # If there's no token provided
            response = {
                "message": "Register or log in to access this resource"
            }
            return make_response(jsonify(response)), 401

        else:
            access_token = auth_header.split(" ")[1]
            # Attempt to decode the token and get the user id
            user_id = User.decode_token(access_token)

            if isinstance(user_id, str):
                # User id does not exist so payload is an error message
                message = user_id
                response = jsonify({
                    "message": message
                })

                response.status_code = 401
                return response

            else:
                return func(user_id=user_id, *args, **kwargs)

    return func_wrapper
