import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import logging
import requests
import pyodbc
from datetime import datetime

app = func.FunctionApp()

# Constants
CITIES = ["Guarulhos", "Curitiba", "Recife", "Seoul", "Sydney", "Paris", "Miami"]
API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Initialize Key Vault client
credential = DefaultAzureCredential()
key_vault_url = "https://engdadoskey2.vault.azure.net/"
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Fetch API key from Key Vault
API_KEY = secret_client.get_secret("api_key").value

def get_db_config():
    return {
        "server": secret_client.get_secret("db-server").value,
        "database": secret_client.get_secret("db-name").value,
        "username": secret_client.get_secret("db-username").value,
        "password": secret_client.get_secret("db-password").value,
    }

def connect_to_sql():
    db_config = get_db_config()
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={db_config['server']};"
        f"Database={db_config['database']};"
        f"Uid={db_config['username']};"
        f"Pwd={db_config['password']};"
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
            try:
                response = requests.get(API_URL, params={
                    "q": city,
                    "appid": API_KEY,
                    "units": "metric"
                })
                response.raise_for_status()
                data = response.json()
                insert_weather_data(conn, data)
                logging.info(f"Processed data for {city}")
            except requests.RequestException as req_err:
                logging.error(f"Request error for {city}: {req_err}")
            except Exception as city_err:
                logging.error(f"Error processing {city}: {city_err}")
        conn.close()
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

# Azure Key Vault Configuration
KEY_VAULT_CONFIG = {
    "type": "setting",
    "settings": {
        "azure.keyVault.name": "engdadoskey2",
        "azure.tenant": "bb19c0d2-edc0-4f29-bc67-6570c6508066",
        "azure.subscription": "feecd42b-a2f9-46bd-8aca-5810ea481805"
    }
}