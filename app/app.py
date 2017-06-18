#!./bl-env/bin/python

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify, request, abort, make_response

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BucketList, Item, User

    app = FlaskAPI(__name__, instance_relative_config="True")
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route("/api/v1/")
    def index():
        return "Welcome"

    @app.route("/api/v1/bucketlists/", methods=["POST", "GET"])
    def bucketlists():
        # Get access token from header
        auth_header = request.headers.get("Authorization")
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the user id
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # The user is authenticated, (the user_id returned is not an
                # error string), handle the request

                if request.method == "POST":
                    name = str(request.data.get("name", ""))
                    if name:
                        bucketlist = BucketList(name=name, created_by=user_id)
                        bucketlist.save()
                        response = jsonify({
                            "id": bucketlist.id,
                            "name": bucketlist.name,
                            "date_created": bucketlist.date_created,
                            "date_modified": bucketlist.date_modified,
                            "created_by": user_id})

                        return make_response(response), 201

                elif request.method == "GET":
                    bucketlists = BucketList.query.filter_by(created_by=user_id)
                    results = []

                    for bucketlist in bucketlists:
                        obj = {
                            "id": bucketlist.id,
                            "name": bucketlist.name,
                            "date_created": bucketlist.date_created,
                            "date_modified": bucketlist.date_modified,
                            "created_by": bucketlist.created_by
                        }
                        results.append(obj)

                    # response = jsonify(results)
                    # response.status_code = 200
                    return make_response(jsonify(results)), 200

            else:
                message = user_id
                response = {
                    "message": message
                }

                return make_response(jsonify(response)), 401

    @app.route("/api/v1/bucketlists/<int:id>/", methods=["GET", "PUT", "DELETE"])
    def bucketlist_manipulation(id, **kwargs):
        # Get access token from header
        auth_header = request.headers.get("Authorization")
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the user id
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # The user is authenticated, (the user_id returned is not an
                # error string), handle the request
                bucketlist = BucketList.query.filter_by(id=id).first()
                if not bucketlist:
                    abort(404)

                if request.method == "DELETE":
                    bucketlist.delete()
                    response = jsonify({
                        "message": "Bucketlist {} has been successfully deleted"
                        .format(bucketlist.name)})
                    response.status_code = 200
                    return response

                elif request.method == "PUT":
                    name = str(request.data.get("name", ""))
                    bucketlist.name = name
                    bucketlist.save()

                    response = jsonify({
                        "id": bucketlist.id,
                        "name": bucketlist.name,
                        "date_created": bucketlist.date_created,
                        "date_modified": bucketlist.date_modified,
                        "created_by": bucketlist.created_by
                    })

                    response.status_code = 200
                    return response

                elif request.method == "GET":
                    response = jsonify({
                        "id": bucketlist.id,
                        "name": bucketlist.name,
                        "date_created": bucketlist.date_created,
                        "date_modified": bucketlist.date_modified,
                        "created_by": bucketlist.created_by
                    })

                    response.status_code = 200
                    return response

            else:
                # User id does not exist so payload is an error message
                message = user_id
                response = {
                    "message": message
                }

                response.status_code = 401
                return response

    @app.route("/api/v1/bucketlists/<int:id>/items/", methods=["POST", "GET"])
    def items():
        # Get access token from header
        auth_header = request.headers.get("Authorization")
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the user id
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # The user is authenticated, (the user_id returned is not an
                # error string), handle the request
                bucketlist = BucketList.query.filter_by(id=id).first()
                if not bucketlist:
                    abort(404)

                if request.method == "POST":
                    name = str(request.data.get("name", ""))
                    if name:
                        bucketlist = BucketList(name=name, created_by=user_id)
                        bucketlist.save()
                        response = jsonify({
                            "id": bucketlist.id,
                            "name": bucketlist.name,
                            "date_created": bucketlist.date_created,
                            "date_modified": bucketlist.date_modified,
                            "created_by": user_id})

                        return make_response(response), 201

                elif request.method == "GET":
                    bucketlists = BucketList.query.filter_by(created_by=user_id)
                    results = []

                    for bucketlist in bucketlists:
                        obj = {
                            "id": bucketlist.id,
                            "name": bucketlist.name,
                            "date_created": bucketlist.date_created,
                            "date_modified": bucketlist.date_modified,
                            "created_by": bucketlist.created_by
                        }
                        results.append(obj)

                    # response = jsonify(results)
                    # response.status_code = 200
                    return make_response(jsonify(results)), 200

    @app.route("/api/v1/bucketlists/<int:id>/items/<int:item_id>/", methods=["POST", "GET"])
    def items_manipulation():
        pass


    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
