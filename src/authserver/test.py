import requests
import jwt


r = requests.post('http://localhost:1337/login')
print(r.json())

tok = r.json()['token']

headers = {'Authorization': f'Bearer {tok}'}
r = requests.post('http://localhost:1337/validate', headers=headers)
print(r)
print(r.text)

r = requests.get('http://localhost:1337/pubkey')
print(r)
print(r.text)
