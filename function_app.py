import azure.functions as func
import logging
import requests
import pyodbc
from datetime import datetime

app = func.FunctionApp()

# API Configuration
API_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = "e7e6f79fa9a7412ed6a06afdd03297c2"  

# SQL Azure Configuration
DB_CONFIG = {
    "server": "engdados.database.windows.net",
    "database": "engdados",
    "username": "azure",
    "password": "Jjl3m47C2@#",
}

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

@app.function_name("coletadadosprev")
@app.schedule(schedule="0 0 * * * *", arg_name="mytimer", run_on_startup=True)
def coletadadosprev(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(microsecond=0).isoformat()
    logging.info('Python timer trigger function started at %s', utc_timestamp)

    try:
        conn = connect_to_sql()
        for city in CITIES:
            response = requests.get(API_URL, params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            })
            data = response.json()
            insert_weather_data(conn, data)
            logging.info(f"Processed data for {city}")
        conn.close()
    except Exception as e:
        logging.error(f"Error: {str(e)}")
