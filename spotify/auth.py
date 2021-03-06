import requests
import json
url = 'https://accounts.spotify.com/api/token'
url2 = 'https://api.spotify.com/v1/me/player/currently-playing'

client_id = '6534fadd9a6c41c2b8416ec7d04b7cce'
client_secret = '03f9fe3ef61846a3bc4dfcf7bbff2c13'
redirect_uri = 'http://127.0.0.1:8000/spotify'
scope = 'user-read-private streaming user-read-email user-read-currently-playing'

auth = [
    f"https://accounts.spotify.com/authorize?client_id={client_id}",
    f"&response_type=code&redirect_uri={redirect_uri}",
    F"&scope={scope}"
]
auth = ''.join(auth)
def Auth(code):
    req = requests.post(url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }).json()
    access_token = req.get('access_token')
    req = requests.get(url2,headers={'Authorization':f'Bearer {access_token}'}).json()
    print(json.dumps(str(req)))
    return access_token