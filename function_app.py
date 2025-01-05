import logging
import requests
import pyodbc
from datetime import datetime

# API Configuration
API_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = "e7e6f79fa9a7412ed6a06afdd03297c2"  

# Configurações do SQL Azure
DB_CONFIG = {
    "server": "engdados.database.windows.net",
    "database": "engdados",
    "username": "azure",
    "password": "Jjl3m47C2@#",
}

# Lista de cidades
CITIES = ["Guarulhos", "Curitiba", "Recife", "Seoul", "Sydney", "Paris", "Miami"]

def connect_to_sql():
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={DB_CONFIG['server']};"
        f"Database={DB_CONFIG['database']};"
        f"Uid={DB_CONFIG['username']};"
        f"Pwd={DB_CONFIG['password']};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

def insert_weather_data(conn, data):
    cursor = conn.cursor()
    query = """
        INSERT INTO WeatherData (
            city_name, country, temperature, feels_like, temp_min, temp_max, pressure, humidity, visibility,
            wind_speed, wind_deg, snow_1h, clouds_all, sunrise, sunset, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        data["name"],
        data["sys"]["country"],
        data["main"]["temp"],
        data["main"]["feels_like"],
        data["main"]["temp_min"],
        data["main"]["temp_max"],
        data["main"]["pressure"],
        data["main"]["humidity"],
        data.get("visibility"),
        data["wind"]["speed"],
        data["wind"]["deg"],
        data.get("snow", {}).get("1h"),
        data["clouds"]["all"],
        datetime.fromtimestamp(data["sys"]["sunrise"]),
        datetime.fromtimestamp(data["sys"]["sunset"]),
        datetime.fromtimestamp(data["dt"]),
    ))
    conn.commit()

def fetch_and_save_weather_data(city):
    response = requests.get(API_URL, params={
        "q": city,
        "appid": API_KEY,
        "units": "metric",
    })
    response.raise_for_status()
    return response.json()

def main(mytimer: func.TimerRequest) -> None:
    logging.info("Timer trigger function executed.")

    try:
        conn = connect_to_sql()

        for city in CITIES:
            logging.info(f"Fetching weather data for {city}.")
            try:
                weather_data = fetch_and_save_weather_data(city)
                insert_weather_data(conn, weather_data)
                logging.info(f"Weather data for {city} inserted successfully.")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching data for {city}: {e}")
            except pyodbc.Error as e:
                logging.error(f"Database error for {city}: {e}")
        
        conn.close()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
