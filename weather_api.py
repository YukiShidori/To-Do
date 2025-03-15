import requests

# Replace with your actual API key
API_KEY = 'DUMMY'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

def get_weather(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  # You can change this to 'imperial' for Fahrenheit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
