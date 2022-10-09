import sys
from time import sleep
import yaml
import os
import requests

from flask import Flask
from flask_restful import Resource, Api
from flask import request
import jwt
from jwcrypto.jwk import JWK

app = Flask(__name__)
api = Api(app)

with open('topology.yaml', 'r') as f:
    topology = yaml.safe_load(f.read())

if 'ECHO_NAME' not in os.environ:
    print('Error: Echo server needs ECHO_NAME env variable')
    sys.exit(1)

echo_name = os.environ['ECHO_NAME']

if echo_name not in topology:
    print(
        f'Error: ECHO_NAME {echo_name} is not present in the topology specification')
    sys.exit(1)

called_echos = topology[echo_name]['calls']
print(called_echos)

# get the public key
if 'AUTH_ENDPOINT' not in os.environ:
    print('Error: Echo server needs AUTH_ENDPOINT env variable')
    sys.exit(1)


acquired_public_key = False
for i in range(100):
    try:
        r = requests.get(f'{os.environ["AUTH_ENDPOINT"]}/pubkey')
    except:
        print(f'pubkey retrieval attempt {i} failed')
        sleep(2)
        continue

    if r.status_code == 200:
        body = r.text
        key = JWK.from_json(body)
        pub_key = key.export_to_pem()
        break
    else:
        print('Failed to contact the auth server')
        sys.exit(1)


class EchoResource(Resource):
    def post(self):
        if not 'Authorization' in request.headers:
            return {'message': 'invalid authorization token'}, 401

        parts = request.headers['Authorization'].split(' ', 1)
        if not parts[0] == 'Bearer':
            return {'message': 'invalid authorization token'}, 401
        token = parts[1]

        obj = jwt.decode(token, pub_key, algorithm="RS256")
        print(obj)

        echo_responses = []
        for echo in called_echos:
            try:
                echo_response = requests.post(
                    f'http://{echo}/echo', headers=request.headers)
            except:
                echo_responses.append({echo: 'did not responded correctly'})
                continue

            if echo_response.status_code == 200:
                echo_responses.append(echo_response.json())

        return {echo_name: echo_responses}


api.add_resource(EchoResource, '/echo')

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
