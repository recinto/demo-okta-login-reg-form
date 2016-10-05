import requests
import json
import config
import traceback

from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from requests.packages.urllib3.exceptions import SNIMissingWarning


class OktaUtil:
    # TODO: This should be configuration driven
    REST_HOST = None
    REST_TOKEN = None
    OKTA_SESSION_ID_KEY = "okta_session_id"
    OKTA_SESSION_TOKEN_KEY = "okta_session_id"
    DEVICE_TOKEN = None
    OKTA_HEADERS = {}

    def __init__(self, headers):
        # This is to supress the warnings for the older version
        requests.packages.urllib3.disable_warnings((InsecurePlatformWarning, SNIMissingWarning))

        self.REST_HOST = config.okta_host_config["host"]
        self.REST_TOKEN = config.okta_host_config["api_key"]
        self.DEVICE_TOKEN = config.okta_host_config["device_token"]

        self.OKTA_HEADERS = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "SSWS {api_token}".format(api_token=self.REST_TOKEN),
            "User-Agent": headers["User-Agent"],
            "X-Forwarded-For": headers["X-Forwarded-For"],
            "X-Forwarded-Port": headers["X-Forwarded-Port"],
            "X-Forwarded-Proto": headers["X-Forwarded-Proto"]
        }


    def authenticate(self, username, password):
        print("authenticate()")
        url = "{host}/api/v1/authn".format(host=self.REST_HOST)

        body = {
            "username": username,
            "password": password,
            "options": {
                "multiOptionalFactorEnroll": True,
                "warnBeforePasswordExpired": True
            },
            "context": {
                "deviceToken": self.DEVICE_TOKEN
            }
        }

        return self.execute_post(url, body)

    def list_factors(self, user_id):
        url = "{host}/api/v1/users/{user_id}/factors".format(host=self.REST_HOST, user_id=user_id)
        body = {}
        return self.execute_get(url, body)

    def push_factor_verification(self, user_id, factor_id):
        url = "{host}/api/v1/users/{user_id}/factors/{factor_id}/verify".format(host=self.REST_HOST, user_id=user_id, factor_id=factor_id)
        body = {}
        return self.execute_post(url, body)

    def factor_verification(self, verify_url, verification_Value):
        body = {"passCode": verification_Value}
        return self.execute_post(verify_url, body)

    def validate_session(self, session_id):
        url = "{host}/api/v1/sessions/{session_id}".format(host=self.REST_HOST, session_id=session_id)
        body = {}
        return self.execute_get(url, body)

    def close_session(self, session_id):
        url = "{host}/api/v1/sessions/{session_id}".format(host=self.REST_HOST, session_id=session_id)
        body = {}
        return self.execute_delete(url, body)

    def create_session(self, session_token):
        url = "{host}/api/v1/sessions?additionalFields=cookieToken".format(host=self.REST_HOST)
        body = {
            "sessionToken": session_token
        }
        return self.execute_post(url, body)

    def get_curent_user(self, session_id):
        session_response = self.validate_session(session_id)
        url = "{host}/api/v1/users/{user_id}".format(host=self.REST_HOST, user_id=session_response["userId"])
        body = {}

        return self.execute_get(url, body)

    def create_user(self, first_name, last_name, email, phone, password):
        print "create_user"
        url = "{host}/api/v1/users?activate=true".format(host=self.REST_HOST)
        body = {
            "profile": {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "login": email,
                "mobilePhone": phone,
            },
            "credentials": {
                "password": {"value": password}
            }
        }

        return self.execute_post(url, body)

    def update_user(self, user_id, first_name, last_name, email, phone, hpsMemberRecords):
        print "update_user"
        url = "{host}/api/v1/users/{user_id}".format(host=self.REST_HOST, user_id=user_id)
        body = {
            "profile": {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "mobilePhone": phone,
                "hpsMemberRecords" : hpsMemberRecords.strip().split(',')
            }
        }

        return self.execute_post(url, body)

    def deactivate_user(self, user_id):
        url = "{host}/api/v1/users/{user_id}/lifecycle/deactivate".format(host=self.REST_HOST, user_id=user_id)
        body = {}

        return self.execute_post(url, body)

    def create_sms_factor(self, user_id, phone_number):
        url = "{host}/api/v1/users/{user_id}/factors?updatePhone=true".format(host=self.REST_HOST, user_id=user_id)

        body = {
            "factorType": "sms",
            "provider": "OKTA",
            "profile": {
                "phoneNumber": phone_number
            }
        }

        return self.execute_post(url, body)

    def activate_sms_factor(self, url, pass_code=None):
        body = {}

        if pass_code:
            body["passCode"] = pass_code

        return self.execute_post(url, body)

    def extend_session(self, url):
        body = {}
        return self.execute_post(url, body)

    def list_users(self, limit):
        url = "{host}/api/v1/users?filter=status eq \"ACTIVE\"&limit={limit}".format(host=self.REST_HOST, limit=limit)
        body = {}
        return self.execute_get(url, body)

    def list_user_schema(self):
        url = "{host}/api/v1/meta/schemas/user/default".format(host=self.REST_HOST)
        body = {}
        return self.execute_get(url, body)

    def reset_hps(self):
        # Get all users
        users = self.list_users(100) # yeah not the greatest... need to make this smarter... this is just here for quick demo purposes
        # set each user's accounts to be blank

        try:
            for user in users:
                user["profile"]["hpsMemberRecords"] = "<a href='javascript:alert(\"Claim Link 1!!!\")'>Claim Link 1</a>,<a href='javascript:alert(\"Claim Link 2!!!\")'>Claim Link 2</a>"
                # update each user
                print "Updating User: " + user["id"]
                self.update_user(
                    user["id"],
                    user["profile"]["firstName"],
                    user["profile"]["lastName"],
                    user["profile"]["email"],
                    user["profile"]["mobilePhone"],
                    user["profile"]["hpsMemberRecords"])

            return {"status":"OK", "message":"all User Member Records set to blank"}
        except:
            traceback.print_exc()
            return {"status":"ERROR", "message":"Failed to reset all member records"}

    def execute_post(self, url, body):
        print url
        print body

        rest_response = requests.post(url, headers=self.OKTA_HEADERS, json=body)
        response_json = rest_response.json()

        # print json.dumps(response_json, indent=4, sort_keys=True)
        return response_json

    def execute_put(self, url, body):
        print url
        print body

        rest_response = requests.put(url, headers=self.OKTA_HEADERS, json=body)
        response_json = rest_response.json()

        # print json.dumps(response_json, indent=4, sort_keys=True)
        return response_json

    def execute_delete(self, url, body):
        print url
        print body

        rest_response = requests.delete(url, headers=self.OKTA_HEADERS, json=body)
        try:
            response_json = rest_response.json()
        except:
            response_json = {"status":"none"}

        # print json.dumps(response_json, indent=4, sort_keys=True)
        return response_json

    def execute_get(self, url, body):
        print url
        print body
        print self.OKTA_HEADERS

        rest_response = requests.get(url, headers=self.OKTA_HEADERS, json=body)
        response_json = rest_response.json()

        # print json.dumps(response_json, indent=4, sort_keys=True)
        return response_json
