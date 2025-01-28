# Aplicativo de Azure Function
Função Azure criada em 4 de janeiro de 2024 para coletar dados meteorológicos da API OpenWeatherMap e armazená-los no Azure SQL Database.

## Recursos
- Coleta dados meteorológicos para cidades predefinidas
- Utiliza a API OpenWeatherMap para informações meteorológicas 
- Armazena dados no Azure SQL Database
- Executa como Função Azure serverless

## Configuração
- Runtime da Função Azure: Python 3.9
- Banco de Dados: Azure SQL
- API: OpenWeatherMap

## Cidades Monitoradas
- Seul
- Sydney
- Paris
- Miami

## Desenvolvimento
Criado para testar a integração de Azure Functions com Azure SQL Database e API OpenWeatherMap.

## Funcionalidade
Esta Função Azure executa as seguintes tarefas:
1. Obtém dados meteorológicos de uma lista predefinida de cidades através da API OpenWeatherMap
2. Registra os dados meteorológicos
3. Armazena os dados meteorológicos no Azure SQL Database

## Autor: Ronaldo Ramires
Criado em: 4 de janeiro de 2024

## Atualizado em:
22 de janeiro de 2024

## Variáveis de Ambiente
```json
{
    "API_KEY": "sua_chave_api_openweathermap",
    "DB_CONFIG": {
        "server": "engdados.database.windows.net",
        "database": "engdados",
        "username": "seu_usuario",
        "password": "sua_senha"
    }
}
