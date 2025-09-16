from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
import requests
import json
import threading
import webbrowser

# In-memory data
users = []
products = []
negotiations = []
transactions = []

govt_schemes = [
    {'name': 'PM-KISAN', 'description': 'Direct income support', 'link': 'https://pmkisan.gov.in/'},
    {'name': 'Pradhan Mantri Fasal Bima Yojana', 'description': 'Crop insurance', 'link': 'https://pmfby.gov.in/'},
]

market_prices = {'wheat': 2000, 'rice': 1800, 'maize': 1500}

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Login', font_size=24, color=(1,1,1,1)))
        self.username = TextInput(hint_text='Username', background_color=(0.2,0.2,0.2,1), foreground_color=(1,1,1,1))
        self.password = TextInput(hint_text='Password', password=True, background_color=(0.2,0.2,0.2,1), foreground_color=(1,1,1,1))
        login_btn = Button(text='Login', background_color=(0,1,1,1))
        login_btn.bind(on_press=self.animate_btn)
        login_btn.bind(on_release=self.login)
        register_btn = Button(text='Register', background_color=(0,1,1,1))
        register_btn.bind(on_press=self.animate_btn)
        register_btn.bind(on_release=self.go_to_register)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_btn)
        layout.add_widget(register_btn)
        self.add_widget(layout)

    def animate_btn(self, instance):
        pass

    def login(self, instance):
        user = next((u for u in users if u['username'] == self.username.text and u['password'] == self.password.text), None)
        if user:
            self.manager.current = 'home'
            self.manager.get_screen('home').role = user['role']
            self.manager.get_screen('home').username = user['username']
        else:
            popup = Popup(title='Error', content=Label(text='Invalid credentials'), size_hint=(0.8, 0.4))
            popup.open()

    def go_to_register(self, instance):
        self.manager.current = 'register'

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Register', font_size=24))
        self.username = TextInput(hint_text='Username')
        self.password = TextInput(hint_text='Password', password=True)
        self.role = Spinner(text='farmer', values=('farmer', 'buyer'))
        register_btn = Button(text='Register')
        register_btn.bind(on_press=self.register)
        back_btn = Button(text='Back to Login')
        back_btn.bind(on_press=self.go_to_login)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(self.role)
        layout.add_widget(register_btn)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def register(self, instance):
        if any(u['username'] == self.username.text for u in users):
            popup = Popup(title='Error', content=Label(text='Username exists'), size_hint=(0.8, 0.4))
            popup.open()
            return
        users.append({'username': self.username.text, 'password': self.password.text, 'role': self.role.text})
        popup = Popup(title='Success', content=Label(text='Registered successfully'), size_hint=(0.8, 0.4))
        popup.open()
        self.manager.current = 'login'

    def go_to_login(self, instance):
        self.manager.current = 'login'

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.welcome_label = Label(text='', font_size=18, color=(1,1,1,1))
        self.layout.add_widget(self.welcome_label)
        self.buttons_layout = GridLayout(cols=2, spacing=10)
        self.layout.add_widget(self.buttons_layout)
        logout_btn = Button(text='Logout', on_press=self.logout, background_color=(0,1,1,1))
        self.layout.add_widget(logout_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        self.welcome_label.text = f'Welcome {self.username}, role: {self.role}'
        self.buttons_layout.clear_widgets()
        self.buttons_layout.add_widget(Button(text='Browse Produce', on_press=self.go_to_browse, background_color=(0,1,1,1)))
        self.buttons_layout.add_widget(Button(text='Transactions', on_press=self.go_to_transactions, background_color=(0,1,1,1)))
        self.buttons_layout.add_widget(Button(text='Weather', on_press=self.go_to_weather, background_color=(0,1,1,1)))
        if self.role == 'farmer':
            self.buttons_layout.add_widget(Button(text='Govt Schemes', on_press=self.go_to_schemes, background_color=(0,1,1,1)))
        self.buttons_layout.add_widget(Button(text='Market Prices', on_press=self.go_to_prices, background_color=(0,1,1,1)))
        if self.role == 'farmer':
            self.buttons_layout.add_widget(Button(text='List Produce', on_press=self.go_to_list, background_color=(0,1,1,1)))

    def go_to_browse(self, instance):
        self.manager.current = 'browse'

    def go_to_list(self, instance):
        self.manager.current = 'list'

    def go_to_transactions(self, instance):
        self.manager.current = 'transactions'

    def go_to_weather(self, instance):
        self.manager.current = 'weather'

    def go_to_schemes(self, instance):
        self.manager.current = 'schemes'

    def go_to_prices(self, instance):
        self.manager.current = 'prices'

    def logout(self, instance):
        self.manager.current = 'login'

class ListProduceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='List Produce', font_size=24))
        self.name_input = TextInput(hint_text='Product Name')
        self.quantity = TextInput(hint_text='Quantity (kg)', input_filter='float')
        self.price = TextInput(hint_text='Price per kg', input_filter='float')
        self.location = TextInput(hint_text='Location')
        list_btn = Button(text='List Product', on_press=self.list_product)
        back_btn = Button(text='Back', on_press=self.go_back)
        layout.add_widget(self.name_input)
        layout.add_widget(self.quantity)
        layout.add_widget(self.price)
        layout.add_widget(self.location)
        layout.add_widget(list_btn)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def list_product(self, instance):
        product_id = len(products) + 1
        products.append({
            'id': product_id,
            'farmer': self.manager.get_screen('home').username,
            'name': self.name_input.text,
            'quantity': float(self.quantity.text),
            'price': float(self.price.text),
            'location': self.location.text
        })
        popup = Popup(title='Success', content=Label(text='Product listed'), size_hint=(0.8, 0.4))
        popup.open()
        self.name_input.text = ''
        self.quantity.text = ''
        self.price.text = ''
        self.location.text = ''


    def go_back(self, instance):
        self.manager.current = 'home'

class BrowseProduceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.layout.add_widget(Label(text='Available Produce', font_size=24))
        self.scroll = ScrollView()
        self.product_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.product_layout.bind(minimum_height=self.product_layout.setter('height'))
        self.scroll.add_widget(self.product_layout)
        self.layout.add_widget(self.scroll)
        back_btn = Button(text='Back', on_press=self.go_back, size_hint_y=None, height=50)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        self.product_layout.clear_widgets()
        for p in products:
            btn = Button(text=f"{p['name']} - {p['quantity']}kg @ ₹{p['price']}/kg in {p['location']}", size_hint_y=None, height=100)
            btn.bind(on_press=lambda instance, pid=p['id']: self.negotiate(pid))
            self.product_layout.add_widget(btn)

    def negotiate(self, product_id):
        self.manager.get_screen('negotiate').product_id = product_id
        self.manager.current = 'negotiate'

    def go_back(self, instance):
        self.manager.current = 'home'

class NegotiateScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.product_label = Label(text='', font_size=18)
        self.layout.add_widget(self.product_label)
        self.offers_label = Label(text='Offers: ')
        self.layout.add_widget(self.offers_label)
        self.offer_input = TextInput(hint_text='Your Offer', input_filter='float')
        submit_btn = Button(text='Submit Offer', on_press=self.submit_offer)
        back_btn = Button(text='Back', on_press=self.go_back)
        self.layout.add_widget(self.offer_input)
        self.layout.add_widget(submit_btn)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        product = next((p for p in products if p['id'] == self.product_id), None)
        if product:
            self.product_label.text = f"{product['name']} - {product['quantity']}kg @ ₹{product['price']}/kg"
            neg = next((n for n in negotiations if n['product_id'] == self.product_id and n['buyer'] == self.manager.get_screen('home').username), None)
            if neg:
                self.offers_label.text = 'Offers: ' + ', '.join(map(str, neg['offers']))
            else:
                neg = {'product_id': self.product_id, 'buyer': self.manager.get_screen('home').username, 'offers': []}
                negotiations.append(neg)
                self.offers_label.text = 'Offers: None'

    def submit_offer(self, instance):
        neg = next((n for n in negotiations if n['product_id'] == self.product_id and n['buyer'] == self.manager.get_screen('home').username), None)
        if neg:
            neg['offers'].append(float(self.offer_input.text))
            self.offers_label.text = 'Offers: ' + ', '.join(map(str, neg['offers']))
            self.offer_input.text = ''

    def go_back(self, instance):
        self.manager.current = 'browse'

class TransactionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Transactions', font_size=24))
        self.scroll = ScrollView()
        self.trans_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.trans_layout.bind(minimum_height=self.trans_layout.setter('height'))
        self.scroll.add_widget(self.trans_layout)
        layout.add_widget(self.scroll)
        back_btn = Button(text='Back', on_press=self.go_back)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def on_enter(self):
        self.trans_layout.clear_widgets()
        username = self.manager.get_screen('home').username
        for t in transactions:
            if t['buyer'] == username or any(p['farmer'] == username for p in products if p['id'] == t['product_id']):
                self.trans_layout.add_widget(Label(text=f"Product {t['product_id']} - ₹{t['amount']} - {t['status']}", size_hint_y=None, height=50))

    def go_back(self, instance):
        self.manager.current = 'home'

class WeatherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Weather', font_size=24, color=(1,1,1,1)))
        self.weather_label = Label(text='Fetching weather...', color=(1,1,1,1))
        layout.add_widget(self.weather_label)
        back_btn = Button(text='Back', on_press=self.go_back, background_color=(0,1,1,1))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def on_enter(self):
        threading.Thread(target=self.fetch_weather).start()

    def fetch_weather(self):
        try:
            response = requests.get('https://wttr.in/Delhi?format=j1')
            data = response.json()
            temp = data['current_condition'][0]['temp_C']
            desc = data['current_condition'][0]['weatherDesc'][0]['value']
            self.weather_label.text = f'Delhi: {temp}°C, {desc}'
        except:
            self.weather_label.text = 'Failed to fetch weather'

    def go_back(self, instance):
        self.manager.current = 'home'

class GovtSchemesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Government Schemes', font_size=24, color=(1,1,1,1)))
        self.scroll = ScrollView()
        self.scheme_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.scheme_layout.bind(minimum_height=self.scheme_layout.setter('height'))
        for s in govt_schemes:
            btn = Button(text=f"{s['name']}: {s['description']}\nClick to visit website", size_hint_y=None, height=100, background_color=(0,1,1,1))
            btn.bind(on_press=lambda instance, link=s['link']: self.open_link(link))
            self.scheme_layout.add_widget(btn)
        self.scroll.add_widget(self.scheme_layout)
        layout.add_widget(self.scroll)
        back_btn = Button(text='Back', on_press=self.go_back, background_color=(0,1,1,1))
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def open_link(self, link):
        webbrowser.open(link)

    def go_back(self, instance):
        self.manager.current = 'home'

class MarketPricesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Market Prices', font_size=24))
        self.scroll = ScrollView()
        self.price_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.price_layout.bind(minimum_height=self.price_layout.setter('height'))
        for item, price in market_prices.items():
            self.price_layout.add_widget(Label(text=f"{item}: ₹{price}/quintal", size_hint_y=None, height=50))
        self.scroll.add_widget(self.price_layout)
        layout.add_widget(self.scroll)
        back_btn = Button(text='Back', on_press=self.go_back)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = 'home'

class SmartFarmersApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Dark background
        Window.size = (400, 700)  # Mobile size for testing
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ListProduceScreen(name='list'))
        sm.add_widget(BrowseProduceScreen(name='browse'))
        sm.add_widget(NegotiateScreen(name='negotiate'))
        sm.add_widget(TransactionsScreen(name='transactions'))
        sm.add_widget(WeatherScreen(name='weather'))
        sm.add_widget(GovtSchemesScreen(name='schemes'))
        sm.add_widget(MarketPricesScreen(name='prices'))
        return sm

if __name__ == '__main__':
    SmartFarmersApp().run()
