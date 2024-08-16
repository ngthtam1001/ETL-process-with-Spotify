from flask import Flask, request, redirect
import requests
import base64

app = Flask(__name__)

CLIENT_ID = '1189ac17baa54891aef7449f507447b6'
CLIENT_SECRET = 'aa54cd9dd6fb4ed08323ca8c1e29e876'
REDIRECT_URI = 'http://localhost:3000/callback'

def get_access_token(authorization_code):
    endpoint = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    payload = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(endpoint, headers=headers, data=payload)
    access_token = response.json().get("access_token")
    return access_token

@app.route('/')
def home():
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=user-read-recently-played"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    access_token = get_access_token(code)
    return f"Access token: {access_token}"

if __name__ == '__main__':
    app.run(debug=True, port=3000)
