from functools import wraps
from flask import Blueprint, request, jsonify


def all_access_level():
    return {
        "0": admin_role(),
        "1": doctor_role(),
        "2": patient_role()
        # "3": guest_role()
    }


def get_module_permission(url):
    module = url.split('/')[-2]
    permission = url.split('/', 2)[-1]
    return module, permission


def admin_role():
    return {
        "doctor": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "patient": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "patient_charge": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "room": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "bed": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "appointment": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "user": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "test_report": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "bill": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "test": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        }
    }


def doctor_role():
    return {
        "doctor": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        },
        "patient": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        },
        "patient_charge": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "room": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        },
        "bed": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        },
        "appointment": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False,
            "approve": False,
            "reject": False
        },
        "test_report": {
            "save": False,
            "edit": True,
            "get": True,
            "list": True,
            "delete": False
        }
    }


def patient_role():
    return {
        "doctor": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        },
        "patient": {
            "save": True,
            "edit": True,
            "get": True,
            "list": False,
            "delete": False
        },
        "patient_charge": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        },
        "appointment": {
            "save": True,
            "edit": True,
            "get": True,
            "list": True,
            "delete": True
        },
        "test_report": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        },
        "bill": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        },
        "test": {
            "save": False,
            "edit": False,
            "get": True,
            "list": True,
            "delete": False
        }
    }


def check_if_authorized(data):
    module, permission = get_module_permission(data.get('url'))
    user_roles = all_access_level()
    if not permission or not user_roles.get(data['role']):
        return dict(status_id=1, response=False)
    return dict(status_id=1, response=user_roles.get(data['role']).get(module).get(permission, False))


def is_authorized(data):
    def decorator(f):
        @wraps(f)
        def wrapped():
            return check_if_authorized(data)

        return wrapped

    return decorator


user_permission_blueprint: Blueprint = Blueprint("user_permission", __name__)


@user_permission_blueprint.route('/check', methods=['POST'])
def check():
    return jsonify(check_if_authorized(request.json))
