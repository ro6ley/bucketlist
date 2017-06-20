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
        # access_token = auth_header.split(" ")[1]

        if auth_header:
            access_token = auth_header.split(" ")[1]
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
                    search_query = str(request.args.get("q", ""))

                    if not search_query:
                        # Paginate results for all bucketlists by default
                        limit = request.args.get("limit")
                        if request.args.get("page"):
                            # Get the page requested
                            page = int(request.args.get("page"))
                        else:
                            # If no page number request, start at the first one
                            page = 1

                        if limit and int(limit) < 100:
                            # Use the limit value from user if it exists
                            limit = int(request.args.get("limit"))
                        else:
                            # Set the default limit value if none was received
                            limit = 10

                        paginated_results = BucketList.query.filter_by(
                            created_by=user_id).paginate(page, limit, False)

                        if paginated_results.has_next:
                            next_page = request.endpoint + '?page=' + str(
                                page + 1) + '&limit=' + str(limit)
                        else:
                            next_page = ""

                        if paginated_results.has_prev:
                            previous_page = request.endpoint + '?page=' + str(
                                page - 1) + '&limit=' + str(limit)
                        else:
                            previous_page = ""

                        paginated_bucketlists = paginated_results.items
                        # Return the bucket lists
                        results = []

                        for bucketlist in paginated_bucketlists:
                            # Get the items in the bucketlists searched
                            items = Item.query.filter_by(
                                bucketlist_id=bucketlist.id)
                            items_list = []

                            for item in items:
                                obj = {
                                    "id": item.id,
                                    "name": item.name,
                                    "date_created": item.date_created,
                                    "date_modified": item.date_modified,
                                    "done": item.done
                                }
                                items_list.append(obj)

                            bucketlist_object = {
                                "id": bucketlist.id,
                                "name": bucketlist.name,
                                "date_created": bucketlist.date_created,
                                "date_modified": bucketlist.date_modified,
                                "items": items_list,
                                "created_by": bucketlist.created_by
                            }
                            results.append(bucketlist_object)

                        response = {
                                "next_page": next_page,
                                "previous_page": previous_page,
                                "bucketlists": results
                            }

                        return make_response(jsonify(response)), 200

                    elif search_query:
                        # If it was a search request
                        search = BucketList.query.filter(
                            BucketList.name.contains(search_query)).all()
                        # If the search has returned any results
                        if search:
                            search_results = []
                            for bucketlist in search:
                                # Get the items in the bucketlists searched
                                items = Item.query.filter_by(
                                    bucketlist_id=bucketlist.id)
                                items_list = []

                                for item in items:
                                    obj = {
                                        "id": item.id,
                                        "name": item.name,
                                        "date_created": item.date_created,
                                        "date_modified": item.date_modified,
                                        "done": item.done
                                        }
                                    items_list.append(obj)

                                bucketlist_object = {
                                    "id": bucketlist.id,
                                    "name": bucketlist.name,
                                    "date_created": bucketlist.date_created,
                                    "date_modified": bucketlist.date_modified,
                                    "items": items_list,
                                    "created_by": bucketlist.created_by
                                }
                                search_results.append(bucketlist_object)

                            return make_response(jsonify(search_results)), 200
                        # If there are no results after the search
                        else:
                            response = {
                                "message": "Bucketlist not found"
                            }
                            return make_response(jsonify(response)), 404

                    else:
                        # If the request was not a search
                        results = []

                        for bucketlist in bucketlists:
                            # Get the items in the bucketlists searched
                            items = Item.query.filter_by(
                                bucketlist_id=bucketlist.id)
                            items_list = []

                            for item in items:
                                obj = {
                                    "id": item.id,
                                    "name": item.name,
                                    "date_created": item.date_created,
                                    "date_modified": item.date_modified,
                                    "done": item.done
                                }
                                items_list.append(obj)

                            bucketlist_object = {
                                "id": bucketlist.id,
                                "name": bucketlist.name,
                                "date_created": bucketlist.date_created,
                                "date_modified": bucketlist.date_modified,
                                "items": items_list,
                                "created_by": bucketlist.created_by
                            }
                            results.append(bucketlist_object)

                        return make_response(jsonify(results)), 200

            else:
                message = user_id
                response = {
                    "message": message
                }

                return make_response(jsonify(response)), 401

        else:
            response = {
                "message": "Register or log in to access this resource"
            }
            return make_response(jsonify(response)), 403

    @app.route("/api/v1/bucketlists/<int:id>/",
               methods=["GET", "PUT", "DELETE"])
    def bucketlist_manipulation(id, **kwargs):
        # Get access token from header
        auth_header = request.headers.get("Authorization")

        if auth_header:
            access_token = auth_header.split(" ")[1]
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
                        "message": "Bucketlist {} has been"
                                   "successfully deleted"
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
                    items = Item.query.filter_by(bucketlist_id=id)
                    items_list = []

                    for item in items:
                        obj = {
                            "id": item.id,
                            "name": item.name,
                            "date_created": item.date_created,
                            "date_modified": item.date_modified,
                            "done": item.done
                        }
                        items_list.append(obj)

                    response = jsonify({
                        "id": bucketlist.id,
                        "name": bucketlist.name,
                        "date_created": bucketlist.date_created,
                        "date_modified": bucketlist.date_modified,
                        "created_by": bucketlist.created_by,
                        "items": items_list
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

        else:
            response = {
                "message": "Register or log in to access this resource"
            }
            return make_response(jsonify(response)), 403

    @app.route("/api/v1/bucketlists/<int:id>/items/", methods=["POST", "GET"])
    def items(id):
        # Get access token from header
        auth_header = request.headers.get("Authorization")

        if auth_header:
            access_token = auth_header.split(" ")[1]
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
                        item = Item(name=name, bucketlist_id=id)
                        item.save()
                        response = jsonify({
                            "id": item.id,
                            "name": item.name,
                            "date_created": item.date_created,
                            "date_modified": item.date_modified,
                            "bucketlist_id": item.bucketlist_id,
                            "created_by": user_id,
                            "done": item.done})

                        return make_response(response), 201

                elif request.method == "GET":
                    items = Item.query.filter_by(bucketlist_id=id)
                    results = []

                    for item in items:
                        obj = {
                            "id": item.id,
                            "name": item.name,
                            "date_created": item.date_created,
                            "date_modified": item.date_modified,
                            "bucketlist_id": item.bucketlist_id,
                            "done": item.done
                        }
                        results.append(obj)

                    # response = jsonify(results)
                    # response.status_code = 200
                    return make_response(jsonify(results)), 200

            else:
                # User id does not exist so payload is an error message
                message = user_id
                response = {
                    "message": message
                }

                response.status_code = 401
                return response

        else:
            response = {
                "message": "Register or log in to access this resource"
            }
            return make_response(jsonify(response)), 403

    @app.route("/api/v1/bucketlists/<int:id>/items/<int:item_id>/",
               methods=["GET", "PUT", "DELETE"])
    def items_manipulation(id, item_id, **kwargs):
        # Get access token from header
        auth_header = request.headers.get("Authorization")

        if auth_header:
            access_token = auth_header.split(" ")[1]
            # Attempt to decode the token and get the user id
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # The user is authenticated, (the user_id returned is not an
                # error string), handle the request
                item = Item.query.filter_by(bucketlist_id=id).filter_by(
                    id=item_id).first()
                if not item:
                    abort(404)

                if request.method == "DELETE":
                    item.delete()
                    response = jsonify({
                        "message": "Item {} has been successfully deleted"
                        .format(item.name)})
                    response.status_code = 200
                    return response

                elif request.method == "PUT":
                    name = str(request.data.get("name", ""))
                    done = str(request.data.get("done", ""))
                    if name:
                        item.name = name
                        item.save()
                        response = jsonify({
                            "id": item.id,
                            "name": item.name,
                            "date_created": item.date_created,
                            "date_modified": item.date_modified,
                            "bucketlist_id": item.bucketlist_id,
                            "created_by": user_id,
                            "done": item.done})

                        return make_response(response), 200

                    elif done:
                        item.done = done
                        item.save()
                        response = jsonify({
                            "id": item.id,
                            "name": item.name,
                            "date_created": item.date_created,
                            "date_modified": item.date_modified,
                            "bucketlist_id": item.bucketlist_id,
                            "created_by": user_id,
                            "done": item.done})

                        return make_response(response), 200

                elif request.method == "GET":
                    all_items = Item.query.filter_by(id=item_id)
                    results = []

                    for item in all_items:
                        obj = {
                            "id": item.id,
                            "name": item.name,
                            "date_created": item.date_created,
                            "date_modified": item.date_modified,
                            "bucketlist_id": item.bucketlist_id,
                            "done": item.done
                        }
                        results.append(obj)

                    return make_response(jsonify(results)), 200

        else:
            response = {
                "message": "Register or log in to access this resource"
            }
            return make_response(jsonify(response)), 403

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
