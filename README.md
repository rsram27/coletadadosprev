# Azure Function App

Azure Function created on January 4, 2024, to collect weather data from OpenWeatherMap API and store it in Azure SQL Database.

## Features
- Collects weather data for predefined cities
- Uses OpenWeatherMap API for weather information
- Stores data in Azure SQL Database
- Runs as serverless Azure Function

## Configuration
- Azure Function runtime: Python 3.9
- Database: Azure SQL
- API: OpenWeatherMap

## Cities Monitored
- Seoul
- Sydney
- Paris
- Miami

## Development
Created for testing Azure Functions integration with Azure SQL Database and OpenWeatherMap API.

## Functionality
This Azure Function App performs the following tasks:
1. Fetches weather data for a list of predefined cities from the OpenWeatherMap API.
2. Logs the weather data.
3. Stores the weather data in an Azure SQL Database.

## Author : Ronaldo Ramires
Created on: January 4, 2024

## Updated on:
January 22, 2024

## Environment Variables
```json
{
    "API_KEY": "your_openweathermap_api_key",
    "DB_CONFIG": {
        "server": "engdados.database.windows.net",
        "database": "engdados",
        "username": "your_username",
        "password": "your_password"
    }
}
