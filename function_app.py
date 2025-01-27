import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import logging
import requests
import pyodbc
from datetime import datetime

app = func.FunctionApp()

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Constantes
CIDADES = ["Guarulhos", "Curitiba", "Recife", "Seoul", "Sydney", "Paris", "Miami"]
URL_API = "https://api.openweathermap.org/data/2.5/weather"

# Inicializa o cliente do Key Vault
try:
    credencial = DefaultAzureCredential()
    url_key_vault = "https://engdadoskey2.vault.azure.net/"
    cliente_secreto = SecretClient(vault_url=url_key_vault, credential=credencial)
    logging.info("Cliente do Key Vault inicializado com sucesso.")
except Exception as e:
    logging.error(f"Erro ao inicializar o cliente do Key Vault: {e}")

# Busca a chave da API no Key Vault
try:
    CHAVE_API = cliente_secreto.get_secret("api_key").value
    logging.info("Chave da API obtida com sucesso.")
except Exception as e:
    logging.error(f"Erro ao obter a chave da API: {e}")

def obter_configuracao_db():
    try:
        config = {
            "servidor": cliente_secreto.get_secret("db-server").value,
            "banco_de_dados": cliente_secreto.get_secret("db-name").value,
            "usuario": cliente_secreto.get_secret("db-username").value,
            "senha": cliente_secreto.get_secret("db-password").value,
        }
        logging.info("Configuração do banco de dados obtida com sucesso.")
        return config
    except Exception as e:
        logging.error(f"Erro ao obter a configuração do banco de dados: {e}")
        return None

def connect_to_sql():
    config = obter_configuracao_db()
    if config is None:
        return None
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['servidor']};"
            f"DATABASE={config['banco_de_dados']};"
            f"UID={config['usuario']};"
            f"PWD={config['senha']}"
        )
        logging.info("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def insert_weather_data(conn, data):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO WeatherData (city, temperature, humidity, pressure, wind_speed, wind_deg, snow_1h, clouds_all, sunrise, sunset, dt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["main"]["temp"],
        data["main"]["humidity"],
        data["main"]["pressure"],
        data["wind"]["speed"],
        data["wind"]["deg"],
        data.get("snow", {}).get("1h"),
        data["clouds"]["all"],
        datetime.fromtimestamp(data["sys"]["sunrise"]),
        datetime.fromtimestamp(data["sys"]["sunset"]),
        datetime.fromtimestamp(data["dt"]),
    ))
    conn.commit()

@app.function_name("WeatherDataCollector")
@app.schedule(schedule="0 */1 * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def main(myTimer: func.TimerRequest) -> None:
    try:
        # Initialize database connection
        conn = None
        utc_timestamp = datetime.utcnow().replace(microsecond=0).isoformat()
        logging.info('Python timer trigger function started at %s', utc_timestamp)

        try:
            conn = connect_to_sql()
            if conn is None:
                logging.error("Não foi possível conectar ao banco de dados.")
                return
            for city in CIDADES:
                try:
                    response = requests.get(URL_API, params={
                        "q": city,
                        "appid": CHAVE_API,
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
        
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        raise  # Re-raise the exception for Azure Functions logging
    finally:
        if conn and not conn.closed:
            conn.close()
            logging.info("Database connection closed")

# Azure Key Vault Configuration
KEY_VAULT_CONFIG = {
    "type": "setting",
    "settings": {
        "azure.keyVault.name": "engdadoskey2",
        "azure.tenant": "bb19c0d2-edc0-4f29-bc67-6570c6508066",
        "azure.subscription": "feecd42b-a2f9-46bd-8aca-5810ea481805"
    }
}