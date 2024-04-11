import time
from flask import Flask, request, jsonify
from auth0.v3.authentication.token_verifier import TokenVerifier, AsymmetricSignatureVerifier
import jwt
import requests
import secretify
import json
from dotenv import load_dotenv
import os

load_dotenv()

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
ALGORITHMS = ['RS256']
AUTHENTICATED = False
AUTH_URL=""

flaskapp =  Flask(__name__)

current_user = None
token_payload = None
device_code_data = None

def validate_token(id_token):
    """
    Verify the token and its precedence

    :param id_token:
    """
    jwks_url = 'https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN)
    issuer = 'https://{}/'.format(AUTH0_DOMAIN)
    sv = AsymmetricSignatureVerifier(jwks_url)
    tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=AUTH0_CLIENT_ID)
    tv.verify(id_token)

@flaskapp.route("/login")
def login():
    """
    Runs the device authorization flow and stores the user object in memory
    """
    device_code_payload = {
        'client_id': AUTH0_CLIENT_ID,
        'scope': 'openid profile'
    }
    device_code_response = requests.post('https://{}/oauth/device/code'.format(AUTH0_DOMAIN), data=device_code_payload)

    if device_code_response.status_code != 200:
        print('Error generating the device code')
        return "False", 403
    
    print('Device code successful')
    global device_code_data
    device_code_data = device_code_response.json()
    AUTH_URL = device_code_data['verification_uri_complete']
    global token_payload 
    token_payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code_data['device_code'],
        'client_id': AUTH0_CLIENT_ID
    }
    return AUTH_URL

@flaskapp.route("/token")
def check_auth():
    """
    Checks if the user has completed the authorization process and determines if the user is aithenticated or not
    """
    AUTHENTICATED = False
    print('Checking if the user completed the flow...')
    while not AUTHENTICATED:
        token_response = requests.post('https://{}/oauth/token'.format(AUTH0_DOMAIN), data=token_payload)

        token_data = token_response.json()
        if token_response.status_code == 200:
            print('Authenticated!')
            print('- Id Token: {}...'.format(token_data['id_token'][:10]))

            validate_token(token_data['id_token'])
            global current_user
            current_user = jwt.decode(token_data['id_token'], algorithms=ALGORITHMS, options={"verify_signature": False})

            AUTHENTICATED = True
            return token_data, 200
        elif token_data['error'] not in ('authorization_pending', 'slow_down'):
            print(token_data['error_description'])
            return "Authorization failed"
            
        else:
            time.sleep(device_code_data['interval'])

@flaskapp.route("/getplain", methods = ['POST'])
def getplaintext():
    """
    Gets the user specified plaintext if the supplied password is correct.
    """
    req = json.loads(request.data.decode("utf-8"))
    try:
        validate_token(req["id_token"])
        plaintext = {"Plaintext": secretify.decrypt(req["Filename"], req["Password"]).decode("utf-8")}
        return jsonify(plaintext), 200
    except Exception as e:
        print(e)
        return "Failed", 403

@flaskapp.route("/getcipher", methods = ['POST'])
def getciphertext():
    """
    Gets the user specified ciphertext if the supplied password is correct
    """
    req = json.loads(request.data.decode("utf-8"))
    try:
        validate_token(req["id_token"])
        res = {"Cipher": secretify.fetch(req["Filename"])}
        return jsonify(res), 200
    except Exception as e:
        print(e)
        return "Failed", 403
    
@flaskapp.route("/setplain", methods = ['POST'])
def setplaintext():
    """
    stores user specified plaintext as an AES-256-GCM cipher with the password as a key using PBKDF
    """
    req = json.loads(request.data.decode("utf-8"))
    try:
        validate_token(req["id_token"])
        secretify.encrypt(req["Filename"], req["Message"], req["Password"])
        return "True", 200
    except Exception as e:
        print(e)
        return "Failed", 403

if __name__ == "__main__":
    flaskapp.run(host=os.getenv("HOST"), port=os.getenv("PORT"))
