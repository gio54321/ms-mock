import requests
import sys


url = sys.argv[1]
print(url)

r = requests.post(f'{url}/login', verify=False)
print(r, r.text)
print(r.json())

tok = r.json()['token']

headers = {'Authorization': f'Bearer {tok}'}
r = requests.post(f'{url}/echo1', verify=False)
print(r, r.text)

r = requests.post(f'{url}/echo1', headers=headers, verify=False)
print(r, r.text)


r = requests.post(f'{url}/echo2')
print(r, r.text)
r = requests.post(f'{url}/echo2', headers=headers, verify=False)
print(r, r.text)
