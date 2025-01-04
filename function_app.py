import azure.functions as func
import datetime
import json
import logging
import requests

app = func.FunctionApp()

# API Configuration
API_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = "e7e6f79fa9a7412ed6a06afdd03297c2"  

@app.route(route="coletadadosprev", auth_level=func.AuthLevel.FUNCTION)
def coletadadosprev(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get city parameter from request
    city = req.params.get('city')
    if not city:
        try:
            req_body = req.get_json()
            city = req_body.get('city')
        except ValueError:
            pass

    if not city:
        return func.HttpResponse(
            "Please provide a city parameter in the query string or request body.",
            status_code=400
        )

    # Make request to OpenWeatherMap API
    try:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()

        # Return weather data as JSON
        return func.HttpResponse(
            body=json.dumps(weather_data),
            mimetype="application/json",
            status_code=200
        )

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data: {str(e)}")
        return func.HttpResponse(
            "Error fetching weather data",
            status_code=500
        )