#!./bl-env/bin/python

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify, request, abort, make_response, redirect
from flask_cors import CORS

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import BucketList, Item, User
    from app.decorator import check_auth

    app = FlaskAPI(__name__, instance_relative_config="True")
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.url_map.strict_slashes = False
    CORS(app, resources=r'/*')
    db.init_app(app)

    @app.route("/")
    def home():
        return redirect('http://docs.bucketlist11.apiary.io')


    @app.route("/api/v1/bucketlists/", methods=["POST", "GET"])
    @check_auth
    def bucketlists(user_id, *args, **kwargs):
        if request.method == "POST":
            all_bucketlists = [bucketlist.name for bucketlist in 
            BucketList.query.filter_by(created_by=user_id)]
            name = str(request.data.get("name", ""))
            if name and name not in all_bucketlists:
                bucketlist = BucketList(name=name, created_by=user_id)
                bucketlist.save()
                response = jsonify({
                    "id": bucketlist.id,
                    "name": bucketlist.name,
                    "date_created": bucketlist.date_created,
                    "date_modified": bucketlist.date_modified,
                    "created_by": user_id})

                return make_response(response), 201

            elif name in all_bucketlists:
                response = jsonify({
                                   "message": "Bucket List already exists"
                                   })
                return make_response(response), 409

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
                # Paginate search results for bucket lists
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

                paginated_results = BucketList.query.filter(
                    BucketList.name.ilike('%'+search_query+'%')).filter_by(
                    created_by=user_id).paginate(page, limit, False)

                if paginated_results.items:

                    if paginated_results.has_next:
                        next_page = request.endpoint + '?q=' + search_query + \
                         '&page=' + str(page + 1) + '&limit=' + str(limit)
                    else:
                        next_page = ""

                    if paginated_results.has_prev:
                        previous_page = request.endpoint + '?q=' + search_query\
                         + '&page=' + str(page - 1) + '&limit=' + str(limit)
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

                # If there are no results after the search
                else:
                    response = {
                        "message": "No results found",
                        "bucketlists": []
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

    @app.route("/api/v1/bucketlists/<int:id>/",
               methods=["GET", "PUT", "DELETE"])
    @check_auth
    def bucketlist_manipulation(id, user_id, *args, **kwargs):
        bucketlist = BucketList.query.filter_by(id=id).first()
        if not bucketlist:
            abort(404)

        if request.method == "DELETE":
            bucketlist.delete()
            response = jsonify({
                "message": "Bucketlist {} has been"
                           "successfully deleted"
                .format(bucketlist.name)})
            response.status_code = 204
            return response

        elif request.method == "PUT":
            all_bucketlists = [bucketlist.name for bucketlist in 
                                BucketList.query.filter_by(created_by=user_id)]

            name = str(request.data.get("name", ""))
            if name not in all_bucketlists:
                bucketlist.name = name
                bucketlist.save()

                response = jsonify({
                    "id": bucketlist.id,
                    "name": bucketlist.name,
                    "date_created": bucketlist.date_created,
                    "date_modified": bucketlist.date_modified,
                    "created_by": bucketlist.created_by
                })

                response.status_code = 201
                return response

            else:
                response = jsonify({
                    "message": "There is an existing bucketlist with the same name. Try again"
                                   })
                response.status_code = 409
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

    @app.route("/api/v1/bucketlists/<int:id>/items/", methods=["POST", "GET"])
    @check_auth
    def items(id, user_id, *args, **kwargs):
        bucketlist = BucketList.query.filter_by(id=id).first()
        if not bucketlist:
            abort(404)

        if request.method == "POST":
            name = str(request.data.get("name", ""))
            all_items_names = [item.name for item in Item.query.filter_by(bucketlist_id=id)]
            if name and name not in all_items_names:
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

            elif name in all_items_names:
                response = jsonify({
                                   "message": "Item already exists"
                                   })
                return make_response(response), 409


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

            return make_response(jsonify(results)), 200

    @app.route("/api/v1/bucketlists/<int:id>/items/<int:item_id>/",
               methods=["GET", "PUT", "DELETE"])
    @check_auth
    def items_manipulation(id, item_id, user_id, *args, **kwargs):
        item = Item.query.filter_by(bucketlist_id=id).filter_by(
                    id=item_id).first()
        if not item:
            abort(404)

        if request.method == "DELETE":
            item.delete()
            response = jsonify({
                "message": "Item {} has been successfully deleted"
                .format(item.name)})
            response.status_code = 204
            return response

        elif request.method == "PUT":
            name = str(request.data.get("name", ""))
            done = str(request.data.get("done", ""))
            all_items = [item.name for item in 
                                Item.query.filter_by(bucketlist_id=id)]
            if name and name not in all_items:
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

                return make_response(response), 201

            elif name in all_items:
                response = jsonify({
                    "message": "There is an existing item with the same name. Try again"
                                   })
                response.status_code = 409
                return response

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

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
