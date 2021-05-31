from datetime import datetime
from re import match, search
from flask import request, jsonify, session, current_app, g

from hospital_management.utils.user_permissions import check_if_authorized
from hospital_management.utils.helpers import decrypt_auth_token


def before_request():
    """ before request"""
    session['start_time'] = datetime.utcnow()
    try:
        if request.method not in ["OPTIONS"]:
            if match(r"^/admin/.*$", request.path) and request.cookies.get("Token"):
                pass
            elif search("/auth", request.path):
                pass
            elif match(r"^/apidocs.*$", request.path):
                pass
            elif match(r"^/flasgger_static/.*$", request.path):
                pass
            elif match(r"^/favicon.ico", request.path):
                pass
            elif match(r"^/apispec.*$", request.path):
                pass
            else:
                session["user_id"] = request.headers.get("user_id")
                if current_app.config['TESTING']:
                    current_app.config['MONGO_DB_NAME'] = 'test'
                from hospital_management.user.handler import UserHandler
                user = UserHandler(user_id=session["user_id"]).get_logged_in_user()
                if not user[0].get("status_id"):
                    return jsonify(user[0]), user[1]
                user = user[0]['response']
                session['access_level'] = user['user'].get("access_level")

                data = dict(url=request.path, role=session['access_level'])
                # Add any URL if needed to bypass.
                if not search("/get_loggedin_user", request.path):
                    result = check_if_authorized(data)
                    if not result.get('response'):
                        return jsonify(dict(status_id=0, reason="Access Denied.")), 403

    except Exception as e:
        import traceback
        current_app.logger.error(traceback.format_exc().splitlines())
        current_app.logger.error('Exception in Interceptor..:{0}'.format(str(e)))
        return jsonify(dict(status_id=0, reason="Token is invalid")), 403


def after_request(response):
    if match(r"^/apidocs/.*$", request.path):
        return response
    elif match(r"^/flasgger_static/.*$", request.path):
        return response
    elif match(r"^/favicon.ico", request.path):
        return response
    elif match(r"^/apispec.*$", request.path):
        return response
    elif match(r"^/admin/.*$", request.path) and request.cookies.get("Token"):
        return response

    elif request.method not in ["OPTIONS"] and ('db' in g):
        if g.db and g.db.session and not g.db.session.has_ended:
            if response.json and 'status_id' in response.json.keys() and response.json['status_id'] in [0, 2]:
                g.db.session.abort_transaction()
            else:
                g.db.session.commit_transaction()
            g.db.session.end_session()

    if session.get('start_time'):
        time_taken = (datetime.utcnow() - session['start_time']).total_seconds()
        current_app.logger.error("Time Taken for API {} : {}s".format(request.path, time_taken))
    else:
        current_app.logger.error("Time Taken for API {} : {}s".format(request.path, '----'))

    return response
