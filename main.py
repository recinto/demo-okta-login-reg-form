import os
import json

from flask import Flask, request, session, send_from_directory
from utils.rest import OktaUtil


app = Flask(__name__)
app.secret_key = "6w_#w*~AVts3!*yd&C]jP0(x_1ssd]MVgzfAw8%fF+c@|ih0s1H&yZQC&-u~O[--"  # For the session


@app.route("/", methods=["GET"])
def root():
    return app.send_static_file("index.html")

@app.route("/admin", methods=["GET"])
def admin():
    # TODO: apply rules to restrict access
    return app.send_static_file("admin.html")

@app.route("/admin/users", methods=["GET"])
def list_users():
    okta_util = OktaUtil(request.headers)

    user_list = okta_util.list_users(100) #  TODO: make this configurable

    return json.dumps(user_list)

@app.route("/admin/users", methods=["POST"])
def create_user():
    print "create_user"
    okta_util = OktaUtil(request.headers)

    first_name = request.form["firstName"]
    last_name = request.form["lastName"]
    email = request.form["email"]
    mobile = request.form["mobile"]
    password = request.form["password"]

    user_info = okta_util.create_user(first_name=first_name,
                                      last_name=last_name,
                                      email=email,
                                      phone=mobile,
                                      password=password)

    return json.dumps(user_info)


@app.route("/admin/usersx/<user_id>", methods=["POST"])
def update_user(user_id):
    print "update_user"
    okta_util = OktaUtil(request.headers)

    first_name = request.form["firstName"]
    last_name = request.form["lastName"]
    email = request.form["email"]
    mobile = request.form["mobile"]
    hpsMemberRecords = request.form["hpsMemberRecords"]

    user_info = okta_util.update_user(user_id=user_id,
                                      first_name=first_name,
                                      last_name=last_name,
                                      email=email,
                                      phone=mobile,
                                      hpsMemberRecords=hpsMemberRecords)

    return json.dumps(user_info)

@app.route("/admin/users/<user_id>", methods=["DELETE"])
def deactivate_user(user_id):
    okta_util = OktaUtil(request.headers)

    user_info = okta_util.deactivate_user(user_id=user_id)

    return json.dumps(user_info)

@app.route("/register", methods=["POST"])
def register():

    okta_util = OktaUtil(request.headers)

    first_name = request.form["firstName"]
    last_name = request.form["lastName"]
    email = request.form["email"]
    mobile = request.form["mobile"]
    password = request.form["password"]

    user_info = okta_util.create_user(first_name=first_name,
                                      last_name=last_name,
                                      email=email,
                                      phone=mobile,
                                      password=password)
    print user_info
    user_id = user_info["id"]

    # Authenticate
    auth_response = okta_util.authenticate(username=email, password=password)
    session[okta_util.OKTA_SESSION_TOKEN_KEY] = auth_response["sessionToken"]

    factor_response = okta_util.create_sms_factor(user_id=user_id, phone_number=mobile)
    activate_url = factor_response["_links"]["activate"]["href"]

    # Activate
    activate_response = okta_util.activate_sms_factor(url=activate_url)

    return json.dumps(activate_response)


@app.route("/activate", methods=["POST"])
def activate():
    print "activate()"
    okta_util = OktaUtil(request.headers)
    response = {"factorResult": "FAILED"}

    activate_url = request.form["refurl"]
    pass_code = request.form["passCode"]
    # Verify sms factor
    activate_response = okta_util.activate_sms_factor(url=activate_url, pass_code=pass_code)

    if activate_response["status"] == "ACTIVE":
        response["factorResult"] = "SUCCESS"

    return json.dumps(response)


@app.route("/createsession", methods=["GET"])
def create_session():
    print "create_session()"
    result = {"success": False}

    try:
        okta_util = OktaUtil(request.headers)
        # Create Session
        session_response = okta_util.create_session(session[okta_util.OKTA_SESSION_TOKEN_KEY])
        session[okta_util.OKTA_SESSION_ID_KEY] = session_response["id"]

        url = session_response["_links"]["refresh"]["href"]
        okta_util.extend_session(url)
        result["success"] = True
    except:
        print "failed to create session"

    return json.dumps(result)


@app.route("/isloggedin", methods=["GET"])
def is_logged_in():
    print "is_logged_in()"

    result = {"isLoggedIn": False}

    try:
        okta_util = OktaUtil(request.headers)
        session_response = okta_util.validate_session(session[okta_util.OKTA_SESSION_ID_KEY])
        print session_response
        url = session_response["_links"]["refresh"]["href"]
        okta_util.extend_session(url)
        result["isLoggedIn"] = True
    except:
        print "not logged in"

    return json.dumps(result)


@app.route("/getuser", methods=["GET"])
def get_user():
    print "get_user()"
    response = {}
    try:
        okta_util = OktaUtil(request.headers)
        user_info = okta_util.get_curent_user(session[okta_util.OKTA_SESSION_ID_KEY])
        print json.dumps(user_info, indent=4, sort_keys=False)
        response["firstName"] = user_info["profile"]["firstName"]
        response["lastName"] = user_info["profile"]["lastName"]
        response["hpsMemberRecords"] = user_info["profile"]["hpsMemberRecords"]
    except:
        print "no user logged in"

    return json.dumps(response)


@app.route("/loginMFA", methods=["POST"])
def loginMFA():
    print "loginMFA()"

    okta_util = OktaUtil(request.headers)

    user = request.form["user"]
    pwd = request.form["password"]

    auth = okta_util.authenticate(username=user, password=pwd)
    try:
        session[okta_util.OKTA_SESSION_TOKEN_KEY] = auth["sessionToken"]
        user_id = auth["_embedded"]["user"]["id"]
        factors = okta_util.list_factors(user_id=user_id)
        factor_id = factors[0]["id"]
        push_factor_response = okta_util.push_factor_verification(user_id=user_id, factor_id=factor_id)
    except:
        session[okta_util.OKTA_SESSION_TOKEN_KEY] = None
        user_id = None
        push_factor_response = {"status":"FAILED", "message":"Authentication Failed"}

    return json.dumps(push_factor_response)

@app.route("/login", methods=["POST"])
def login():
    print "login()"

    okta_util = OktaUtil(request.headers)

    user = request.form["user"]
    pwd = request.form["password"]

    auth = okta_util.authenticate(username=user, password=pwd)

    try:
        session[okta_util.OKTA_SESSION_TOKEN_KEY] = auth["sessionToken"]
        user_id = auth["_embedded"]["user"]["id"]
        session_response = okta_util.create_session(session[okta_util.OKTA_SESSION_TOKEN_KEY])
        session[okta_util.OKTA_SESSION_ID_KEY] = session_response["id"]
    except:
        session[okta_util.OKTA_SESSION_TOKEN_KEY] = None
        user_id = None
        session_response = {"status":"FAILED", "message":"Authentication Failed"}

    return json.dumps(session_response)

@app.route("/logout", methods=["GET"])
def logout():
    print "logout()"
    okta_util = OktaUtil(request.headers)
    session_response = okta_util.close_session(session[okta_util.OKTA_SESSION_TOKEN_KEY])
    session[okta_util.OKTA_SESSION_ID_KEY] = None

    return json.dumps(session_response)


@app.route("/verifyFactor", methods=["POST"])
def verifyFactor():
    print "verifyFactor()"

    okta_util = OktaUtil(request.headers)

    verify_url = request.form["refurl"]
    verification_Value = request.form["passCode"]

    factor_response = okta_util.factor_verification(verify_url=verify_url,
                                                    verification_Value=verification_Value)

    session_response = okta_util.create_session(session[okta_util.OKTA_SESSION_TOKEN_KEY])
    session[okta_util.OKTA_SESSION_ID_KEY] = session_response["id"]

    return json.dumps(factor_response)

@app.route("/getuserschema", methods=["GET"])
def get_user_schema():
    print "get_user_schema()"
    okta_util = OktaUtil(request.headers)
    response = okta_util.list_user_schema()
    return json.dumps(response)

@app.route("/resethps", methods=["GET"])
def reset_hps():
    print "reset_hps()"
    okta_util = OktaUtil(request.headers)
    response = okta_util.reset_hps()
    return json.dumps(response)

@app.route('/js/<path:filename>')
def serve_static_js(filename):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static', 'js'), filename)


@app.route('/css/<path:filename>')
def serve_static_css(filename):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static', 'css'), filename)


@app.route('/img/<path:filename>')
def serve_static_img(filename):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static', 'img'), filename)


if __name__ == "__main__":
    # This is to run on c9.io.. you may need to change or make your own runner
    app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)))
