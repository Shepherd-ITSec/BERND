import os
import base64
import hashlib
import requests
import webbrowser
import configparser
from flask import Flask, redirect, request, render_template, jsonify

app = Flask(__name__)

# Load configuration variables from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

CLIENT_ID = config['SECRETS']['CLIENT_ID']
CLIENT_SECRET = config['SECRETS']['CLIENT_SECRET']
REDIRECT_URI = config['DEFAULT']['REDIRECT_URI']
AUTHORIZATION_URL = config['DEFAULT']['AUTHORIZATION_URL']
TOKEN_URL = config['DEFAULT']['TOKEN_URL']
SCOPE = config['DEFAULT']['SCOPE']
RETRY_INTERVAL = int(config['SETTING']['RETRY_INTERVAL'])  # Convert to integer
access_token = None  # Global variable for storing access token

def generate_code_verifier_and_challenge():
    """Generate code verifier and challenge for PKCE flow."""
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

def make_api_request():
    """Make an authenticated request to the API and process the result."""
    API_URL = 'https://tosti.science.ru.nl/api/v1/shifts/?can_order=true'

    api_response = requests.get(API_URL, headers={
        'Authorization': f'Bearer {access_token}'
    })

    if api_response.status_code == 200:
        api_data = api_response.json()
        count = api_data.get('count', 0)

        if count > 0:
            shifts = api_data.get('results', [])

            # Sort shifts by the number of orders to find the one with the least orders
            shifts_sorted = sorted(shifts, key=lambda x: x['amount_of_orders'])
            least_ordered_shift = shifts_sorted[0]
            shift_id = least_ordered_shift['id']
            venue_name = least_ordered_shift['venue']['venue']['name']
            amount_of_orders = least_ordered_shift['amount_of_orders']

            # Post an order to the shift with the least orders
            order_response_1 = post_order_to_shift(shift_id)
            order_response_2 = post_order_to_shift(shift_id)  # Place the same order a second time

            # Check responses
            if order_response_1.status_code == 201 and order_response_2.status_code == 201:
                webbrowser.open(f"https://tosti.science.ru.nl/shifts/{shift_id}/overview/")
                return {
                    'success': True,
                    'message': (f"Successfully placed orders in shift at {venue_name} "
                                f"with {amount_of_orders} orders in front of you.")
                }
            else:
                return {'success': False, 'message': f"Failed to place order: {order_response_1.text} {order_response_2.text}"}
        else:
            return {'success': False, 'message': f"No shifts available yet: {api_response.text}"}
    else:
        return {'success': False, 'message': f"API request failed: {api_response.text}"}

def post_order_to_shift(shift_id):
    """Post an order to the specified shift."""
    ORDER_URL = f"https://tosti.science.ru.nl/api/v1/shifts/{shift_id}/orders/"
    order_data = {
        "product": 2,  # This should be the product ID for tosti ham and cheese
        "ready": False,
        "paid": True,   # makes no difference btw.
        "picked_up": False,
        "type": 0,
        "priority": 1
    }
    response = requests.post(ORDER_URL, json=order_data, headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    })
    return response

@app.route('/')
def home():
    """Generate code verifier and challenge, then redirect user to the authorization URL."""
    global code_verifier
    code_verifier, code_challenge = generate_code_verifier_and_challenge()

    authorization_url = (f"{AUTHORIZATION_URL}?response_type=code"
                         f"&client_id={CLIENT_ID}"
                         f"&redirect_uri={REDIRECT_URI}"
                         f"&scope={SCOPE}"
                         f"&code_challenge={code_challenge}"
                         f"&code_challenge_method=S256")

    return redirect(authorization_url)

@app.route('/callback')
def callback():
    """Handle OAuth callback, exchange authorization code for access token, and redirect to waiting page."""
    global access_token
    code = request.args.get('code')

    token_response = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code_verifier': code_verifier
    })

    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data.get('access_token')

        # Redirect to the waiting page
        return redirect('/waiting')
    else:
        return f'Error retrieving token: {token_response.text}'

@app.route('/waiting')
def waiting():
    """Show the no tosti available message and start the loop to check for shifts."""
    return render_template('waiting.html', retry_interval=RETRY_INTERVAL)

@app.route('/check_tosti')
def check_tosti():
    """Endpoint to check for available tosti orders (used by JavaScript)."""
    result = make_api_request()
    return jsonify(result)

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    webbrowser.open("https://localhost:5000/")
    app.run(ssl_context='adhoc')
