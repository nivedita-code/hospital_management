from datetime import datetime, timedelta
from http import HTTPStatus
import bcrypt
from bson import ObjectId
import uuid

from flask import current_app

from hospital_management.db import get_pymongo_db


class UserHandler:
    def __init__(self, user_id: str = None):
        self.db = get_pymongo_db()
        self.user_id = user_id

    @staticmethod
    def _validate_password(entered_password, password_hash):
        return bcrypt.checkpw(entered_password.encode("utf-8"), password_hash.encode("utf-8"))

    def validate_password(self, data: dict) -> tuple:
        """
        The method, validates's user for entered email_id (has to be a verified email) /user_id /
        phone_number (has to be a verified phone)
        :param request: the request object. to handle login status.
        :param data: request json of login_id and password
        :return: {status_id: 1(success) / 0(fail):int , reason: if fail: str, access_token: if success: str}
                HTTPStatus (400/401/200)
        """
        if not {"user_name", "password"}.issubset(data.keys()):
            return {"status_id": 0, "reason": "Mandatory Keys Missing."}, HTTPStatus.BAD_REQUEST
        user_data = self.db.filter_one_doc(current_app.config['MONGO_DB_NAME'], current_app.config['MONGO_COL_USER'],
                                           {'user_name': data['user_name'].strip()})
        if not user_data:
            return {"status_id": 0, "reason": "Invalid User Name or Password."}, 401
        result = self._validate_password(data.get("password"), user_data.get("password"))
        if not result:
            return {"status_id": 0, "reason": "Invalid Email Id or Password."}, HTTPStatus.UNAUTHORIZED
        return {"status_id": 1, "user_id": user_data["_id"]}, HTTPStatus.OK

    @staticmethod
    def _generate_password_hash(password):
        """

        :param password: password string to hash and save it
        :return: hashed_pwd
        """
        salt = bcrypt.gensalt()
        hashed_pwd = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_pwd

    def add_user(self, data: dict) -> tuple:
        if not {'user_name', 'password', 'first_name', 'last_name', 'date_of_birth', 'phone'}.issubset(set(data.keys())):
            return {'status_id': 0, 'reason': 'Keys Missing.'}, HTTPStatus.BAD_REQUEST
        if self.db.filter_one_doc(current_app.config['MONGO_DB_NAME'], current_app.config['MONGO_COL_USER'],
                                  {'user_name': data['user_name'].strip()}):
            return {'status_id': 0, 'reason': 'User Name Exists.'}, HTTPStatus.BAD_REQUEST
        data['registration_id'] = str(uuid.uuid4())
        if not data.get('access_level'):
            data['access_level'] = '2'
        data['is_active'] = True
        data['password'] = self._generate_password_hash(data['password']).decode("utf-8")
        data['date_of_birth'] = datetime.strptime(data['date_of_birth'], '%d/%m/%Y')
        user = self.db.insert_doc(data, current_app.config['MONGO_DB_NAME'], current_app.config['MONGO_COL_USER'])
        return {'status_id': 1, '_id': user.inserted_id, 'response': "Saved Successfully."}, HTTPStatus.CREATED

    def get_logged_in_user(self, ) -> tuple:
        project_json = {
            'first_name': 1,
            'last_name': 1,
            'middle_name': 1,
            'access_level': 1
        }
        user = self.db.filter_one_doc(current_app.config['MONGO_DB_NAME'], current_app.config['MONGO_COL_USER'],
                               {'_id': ObjectId(self.user_id), 'is_active': True}, project_json)
        if not user:
            return {'status_id': 0, 'reason': 'User Does not Exist'}, HTTPStatus.BAD_REQUEST
        return {'status_id': 1, 'response': {'user': user}}, HTTPStatus.OK
