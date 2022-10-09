from flask import Flask
from flask_restful import Resource, Api
from flask import request
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jwt
from jwcrypto.jwk import JWK
import sys


# generate a rsa key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
pem_private_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)
pem_public_key = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


app = Flask(__name__)
api = Api(app)

tokens = {}


class LoginResource(Resource):
    def post(self):
        new_token = os.urandom(32).hex()
        tokens[new_token] = {
            'role': 'user'
        }
        return {'token': new_token}


class ValidationResource(Resource):
    def post(self):
        print('validate')
        sys.stdout.flush()
        if not 'Authorization' in request.headers:
            return {'message': 'invalid authorization token'}, 401

        parts = request.headers['Authorization'].split(' ', 1)
        if not parts[0] == 'Bearer':
            return {'message': 'invalid authorization token'}, 401
        token = parts[1]
        print(token)
        sys.stdout.flush()

        if not token in tokens:
            return {'message': 'invalid authorization token'}, 401

        user = tokens[token]
        print(user)
        user_claim_token = jwt.encode(
            user, pem_private_key, algorithm="RS256")

        return {'user_claims': user_claim_token.decode('ascii')}


class PubKeyResource(Resource):
    def get(self):
        key = JWK()
        key.import_from_pem(pem_public_key)
        return key.export_public(as_dict=True)


api.add_resource(LoginResource, '/login')
api.add_resource(ValidationResource, '/validate')
api.add_resource(PubKeyResource, '/pubkey')

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
