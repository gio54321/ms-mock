import requests

from flask import Flask
from flask_restful import Resource, Api
from flask import request

app = Flask(__name__)
api = Api(app)


class LoginResource(Resource):
    def post(self):
        auth_res = requests.post(
            'http://authserver/login')
        if not auth_res.status_code == 200:
            return {'message', 'authentication error'}, 401
        return auth_res.json()


def echo(uri, request):
    if not 'Authorization' in request.headers:
        return {'message': 'missing authorization token'}, 401

    print(request.headers['Authorization'])
    # get user claims token
    auth_res = requests.post(
        'http://authserver/validate', headers=request.headers)
    if not auth_res.status_code == 200:
        return {'message': 'invalid authorization token'}, 401

    user_claims = auth_res.json()['user_claims']
    print(user_claims)

    headers = {'Authorization': f'Bearer {user_claims}'}
    echo_response = requests.post(uri, headers=headers)
    if echo_response.status_code != 200:
        return {'message': 'internal error'}, 500

    return echo_response.json()


class Echo1Resource(Resource):
    def post(self):
        return echo('http://echo1/echo', request)


class Echo2Resource(Resource):
    def post(self):
        return echo('http://echo2/echo', request)


api.add_resource(Echo1Resource, '/echo1')
api.add_resource(Echo2Resource, '/echo2')
api.add_resource(LoginResource, '/login')

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
