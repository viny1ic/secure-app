from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from authlib.integrations.flask_client import OAuth
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['AUTH0_DOMAIN'] = 'your-auth0-domain'
app.config['AUTH0_CLIENT_ID'] = 'your-auth0-client-id'
app.config['AUTH0_CLIENT_SECRET'] = 'your-auth0-client-secret'
app.config['AUTH0_API_AUDIENCE'] = 'your-auth0-api-audience'
api = Api(app)
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=app.config['AUTH0_CLIENT_ID'],
    client_secret=app.config['AUTH0_CLIENT_SECRET'],
    api_base_url=f'https://{app.config["AUTH0_DOMAIN"]}',
    access_token_url=f'https://{app.config["AUTH0_DOMAIN"]}/oauth/token',
    authorize_url=f'https://{app.config["AUTH0_DOMAIN"]}/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

def require_scope(scope):
       def decorator(f):
           @wraps(f)
           def decorated(*args, **kwargs):
               token = get_token_auth_header()
               try:
                   payload = auth0.parse_id_token(token)
                   if scope in payload.get('scope', '').split():
                       return f(*args, **kwargs)
                   else:
                       raise AuthError({
                           'code': 'insufficient_scope',
                           'description': 'Permission denied.'
                       }, 403)
               except Exception as e:
                   raise AuthError({
                       'code': 'invalid_token',
                       'description': 'Token is invalid.'
                   }, 401)
           return decorated
       return decorator


def get_token_auth_header():
       auth_header = request.headers.get('Authorization', None)
       if not auth_header:
           raise AuthError({
               'code': 'authorization_header_missing',
               'description': 'Authorization header is expected.'
           }, 401)
       parts = auth_header.split()
       if parts[0].lower() != 'bearer':
           raise AuthError({
               'code': 'invalid_header',
               'description': 'Authorization header must start with "Bearer".'
           }, 401)
       elif len(parts) == 1:
           raise AuthError({
               'code': 'invalid_header',
               'description': 'Token not found.'
           }, 401)
       elif len(parts) > 2:
           raise AuthError({
               'code': 'invalid_header',
               'description': 'Authorization header must be bearer token.'
           }, 401)
       return parts[1]

class AuthLogin(Resource):
       def get(self):
           return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback')
class AuthCallback(Resource):
    def get(self):
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()
        # Perform any additional user validation or database operations here
        return jsonify(userinfo)


api.add_resource(AuthLogin, '/login')
api.add_resource(AuthCallback, '/callback')

class ProtectedResource(Resource):
       @require_scope('read:protected')
       def get(self):
           return {'message': 'Protected resource accessed.'}
api.add_resource(ProtectedResource, '/protected')

if __name__ == '__main__':
       app.run(debug=True)