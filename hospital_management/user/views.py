from flask import jsonify, request, Blueprint, session

from .handler import UserHandler

user_blueprint: Blueprint = Blueprint("/user", __name__)


@user_blueprint.route("/auth", methods=["POST"])
def auth():
    """
        this api is to validate the login details.
        ---
        tags:
            - User
        post:
            consumes:
                - application/json
            produces:
                - application/json
            parameters:
                -   name: request body
                    in: body
                    required: true
                    schema:
                        type: object
                        properties:
                            user_name:
                                type: string
                            password:
                                type: string
                        example:
                            {
                                    "user_name": "sscr27@gmail.com",
                                    "password": "12345678"
                            }


        responses:
            200:
                description: Status ID
                schema:
                    type:
                        object
                    properties:
                        id:
                            type: string
                        response:
                            type: string
                        status_id:
                            type: number
                    example:
                        {
                            "status_id": 1
                        }
        """
    result = UserHandler().validate_password(request.json)
    return jsonify(result[0]), result[1]


@user_blueprint.route("/save", methods=["POST"])
def save_user():
    """
        this api is to validate the login details.
        ---
        tags:
            - User
        post:
            consumes:
                - application/json
            produces:
                - application/json
            parameters:
                -   name: user_id
                    in: header
                    schema:
                        type: string
                        required: true
                -   name: request body
                    in: body
                    required: true
                    schema:
                        type: object
                        properties:
                            login_id:
                                type: string
                            password:
                                type: string
                        example:
                            {
                              "email": "sscr@sscr.com",
                              "first_name": "ojb",
                              "last_name": "iii",
                              "user_name": "name",
                              "password": "12345678",
                              "date_of_birth": "08/12/2000",
                              "phone": {
                                "phone_number": "87878787",
                                "phone_type": "office",
                                "dial_code": "09"
                              }
                            }


        responses:
            200:
                description: Status ID
                schema:
                    type:
                        object
                    properties:
                        id:
                            type: string
                        response:
                            type: string
                        status_id:
                            type: number
                    example:
                        {
                            "status_id": 1
                        }
        """
    result = UserHandler(user_id=session['user_id']).add_user(request.json)
    return jsonify(result[0]), result[1]


@user_blueprint.route("/get_loggedin_user", methods=["POST"])
def get_loggedin_user():
    """
        this api is to validate the login details.
        ---
        tags:
            - User
        post:
            produces:
                - application/json
            parameters:
                -   name: user_id
                    in: header
                    schema:
                      type: string
                      required: true

        responses:
            200:
                description: Status ID
                schema:
                    type:
                        object
                    properties:
                        id:
                            type: string
                        response:
                            type: string
                        status_id:
                            type: number
                    example:
                        {
                            "status_id": 1
                        }
        """
    result = UserHandler(user_id=session['user_id']).get_logged_in_user()
    return jsonify(result[0]), result[1]