from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure key

# In-memory data storage (replace with database later)
users = []  # List of dicts: {'username': str, 'password': str, 'role': 'farmer' or 'buyer'}
products = []  # List of dicts: {'id': int, 'farmer': str, 'name': str, 'quantity': int, 'price': float, 'location': str}
negotiations = []  # List of dicts: {'product_id': int, 'buyer': str, 'offers': list of floats}
transactions = []  # List of dicts: {'id': int, 'product_id': int, 'buyer': str, 'amount': float, 'status': str}

# Mock data for govt schemes and market prices
govt_schemes = [
    {'name': 'PM-KISAN', 'description': 'Direct income support to farmers', 'link': 'https://pmkisan.gov.in/'},
    {'name': 'Pradhan Mantri Fasal Bima Yojana', 'description': 'Crop insurance scheme', 'link': 'https://pmfby.gov.in/'},
]

market_prices = {
    'wheat': 2000,  # per quintal
    'rice': 1800,
    'maize': 1500,
}

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session['username'], role=session['role'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if any(u['username'] == username for u in users):
            flash('Username already exists')
            return redirect(url_for('register'))
        users.append({'username': username, 'password': password, 'role': role})
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('home'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/list_produce', methods=['GET', 'POST'])
def list_produce():
    if 'username' not in session or session['role'] != 'farmer':
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        location = request.form['location']
        product_id = len(products) + 1
        products.append({'id': product_id, 'farmer': session['username'], 'name': name, 'quantity': quantity, 'price': price, 'location': location})
        flash('Product listed successfully')
        return redirect(url_for('list_produce'))
    return render_template('list_produce.html', products=[p for p in products if p['farmer'] == session['username']])

@app.route('/browse_produce')
def browse_produce():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('browse_produce.html', products=products)

@app.route('/negotiate/<int:product_id>', methods=['GET', 'POST'])
def negotiate(product_id):
    if 'username' not in session:
        return redirect(url_for('home'))
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('Product not found')
        return redirect(url_for('browse_produce'))
    neg = next((n for n in negotiations if n['product_id'] == product_id and n['buyer'] == session['username']), None)
    if not neg:
        neg = {'product_id': product_id, 'buyer': session['username'], 'offers': []}
        negotiations.append(neg)
    if request.method == 'POST':
        offer = float(request.form['offer'])
        neg['offers'].append(offer)
        flash('Offer submitted')
        return redirect(url_for('negotiate', product_id=product_id))
    return render_template('negotiate.html', product=product, offers=neg['offers'])

@app.route('/transactions')
def transactions_page():
    if 'username' not in session:
        return redirect(url_for('home'))
    user_transactions = [t for t in transactions if t['buyer'] == session['username'] or any(p['farmer'] == session['username'] for p in products if p['id'] == t['product_id'])]
    return render_template('transactions.html', transactions=user_transactions)

@app.route('/weather')
def weather():
    # Mock weather data (replace with API call)
    weather_data = {
        'location': 'Delhi',
        'temperature': '25°C',
        'description': 'Sunny',
        'podcast': 'Listen to today\'s farming weather update'  # Placeholder for podcast
    }
    # Uncomment below for real API (need API key)
    # api_key = 'your_openweather_api_key'
    # response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q=Delhi&appid={api_key}')
    # if response.status_code == 200:
    #     data = response.json()
    #     weather_data = {
    #         'location': data['name'],
    #         'temperature': f"{data['main']['temp'] - 273.15:.1f}°C",
    #         'description': data['weather'][0]['description']
    #     }
    return render_template('weather.html', weather=weather_data)

@app.route('/govt_schemes')
def govt_schemes_page():
    return render_template('govt_schemes.html', schemes=govt_schemes)

@app.route('/direct_link/<int:product_id>')
def direct_link(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash('Product not found')
        return redirect(url_for('home'))
    link = url_for('negotiate', product_id=product_id, _external=True)
    return render_template('direct_link.html', product=product, link=link)

@app.route('/market_prices')
def market_prices_page():
    # Mock market prices (replace with API call)
    # Uncomment below for real API (need API key)
    # response = requests.get('https://api.agrimarket.com/prices')  # Example API
    # if response.status_code == 200:
    #     market_prices = response.json()
    return render_template('market_prices.html', prices=market_prices)

if __name__ == '__main__':
    app.run(debug=True)
