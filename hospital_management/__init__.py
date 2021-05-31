from datetime import datetime
from functools import wraps

from bson.objectid import ObjectId
from flask import Flask, request, Response, jsonify
from flask.json import JSONEncoder
from flask_cors import CORS
from re import match
from pymongo.command_cursor import CommandCursor
from flask_restx import Api

from hospital_management.utils.request_helpers import before_request, after_request


class CustomJSONEncoder(JSONEncoder):
    """
    Class consist action related to Custom JSON Encoding
    """

    def default(self, obj):
        """
        Method consist of operations performed to encode different data-types into JSON format
        :param obj:
        :return:
        """
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return str(obj)
        if isinstance(obj, CommandCursor):
            return list(obj)
        return JSONEncoder.default(self, obj)


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if match(r"^/apidocs.*$", environ['PATH_INFO']) or match(r"^/flasgger_static/.*$", environ['PATH_INFO']) or \
                match(r"^/favicon.ico", environ['PATH_INFO']) or match(r"^/apispec.*$", environ['PATH_INFO']):
            return self.app(environ, start_response)
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]


def create_app(test_config=None):
    """
    Create Instance of Flask Application
    :param: test_config: Type of config <Test:True, Dev:False>
    """

    """----------------------------------- Create and configure Application  --------------------------------------"""
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        from instance import config
        app.config.from_mapping(
            SECRET_KEY=config.SECRET_KEY,
        )
        version = config.VERSION
    else:
        from instance import test_config
        app.config.from_mapping(
            SECRET_KEY=test_config.SECRET_KEY,
        )
        version = test_config.VERSION
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        app.config['TESTING'] = False
    else:
        # load the test config if passed in
        app.config.from_pyfile('test_config.py', silent=True)
        app.config['TESTING'] = True
    print("Initialized.")

    CORS(app)
    api = Api(app, doc='/{}/'.format(version))
    # app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/{}'.format(version))

    """------------------------------------ Load Customised JSON Encoder -------------------------------------------"""
    app.json_encoder = CustomJSONEncoder

    """------------------------------------ Initialize Database -------------------------------------------"""
    from hospital_management import db
    db.init_app(app)

    with app.app_context():

        """"------------------------------------ Common APIs ---------------------------------------------------"""
        from hospital_management.user import user_blueprint
        # from dc_scm_be.common.order_type.views import order_type_blueprint
        # from dc_scm_be.common.add_ons import addons_blueprint
        # from dc_scm_be.common.combos import combos_blueprint
        # from dc_scm_be.common.products import products_blueprint
        # from dc_scm_be.common.ingredients import ingredients_blueprint
        # from dc_scm_be.common.categories import categories_blueprint
        # from dc_scm_be.common.schema import common_schema_blueprint
        #
        app.register_blueprint(user_blueprint, url_prefix="/{}/user".format(version))
        # app.register_blueprint(order_type_blueprint, url_prefix="/common/order_type")
        # app.register_blueprint(addons_blueprint, url_prefix="/common/add_ons")
        # app.register_blueprint(combos_blueprint, url_prefix="/common/combos")
        # app.register_blueprint(products_blueprint, url_prefix="/common/products")
        # app.register_blueprint(ingredients_blueprint, url_prefix="/common/ingredients")
        # app.register_blueprint(categories_blueprint, url_prefix="/common/categories")
        # app.register_blueprint(common_schema_blueprint, url_prefix="/schema")

        """"------------------------------ Load Before & After Request Logic  ------------------------------------"""
        app.before_request(before_request)
        app.after_request(after_request)

    """"------------------------------ Load Up Swagger for API Docs  --------------------------------------"""
    from flasgger import Swagger
    app.config['SWAGGER'] = {
        'title': 'DigiSCM APIs',
        'uiversion': 3,
        # 'url_prefix': '/{}'.format(version)
    }
    # swagger_config = Swagger.DEFAULT_CONFIG
    # swagger_config['url_prefix'] = '/{}'.format(version)
    Swagger(app, decorators=[requires_basic_auth],
            template={
                "swagger": "2.0",
                "info": {
                    "title": "Hospital Management APIs",
                    "version": app.config["APPLICATION_ROOT"],
                },
                "consumes": [
                    "application/json",
                ],
                "produces": [
                    "application/json",
                ],
                'securityDefinitions': {'basicAuth': {'type': 'basic'}},

            }, )

    """"------------------------------------ Error Handling Logic --------------------------------------------------"""

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({'status_id': 0, 'reason': 'URL not found'}), 404

    from pymongo.errors import OperationFailure
    from hospital_management.utils.helpers import catch_exception
    from hospital_management.utils.helpers import catch_write_conflict_exception
    app.register_error_handler(Exception, catch_exception)
    app.register_error_handler(OperationFailure, catch_write_conflict_exception)

    return app


def requires_basic_auth(f):
    """Decorator to require HTTP Basic Auth for your endpoint."""

    def check_auth(username, password):
        return username == "hospital" and password == "passisnotword"

    def authenticate():
        return Response(
            "Authentication required.", 401,
            {"WWW-Authenticate": "Basic realm='Login Required'"},
        )

    @wraps(f)
    def decorated(*args, **kwargs):
        # NOTE: This example will require Basic Auth only when you run the
        # app directly. For unit tests, we can't block it from getting the
        # Swagger specs so we just allow it to go through without auth.
        # The following two lines of code wouldn't be needed in a normal
        # production environment.

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated
