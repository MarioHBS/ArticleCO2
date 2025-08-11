# MapBiomas Alert API

### MapBiomas Alert API é um cliente Python para o serviço MapBiomas Alert API.

MapBiomas Alert é um sistema que valida e refina alertas de desmatamento com imagens de alta resolução. Em uma plataforma gratuita e de acesso aberto, o serviço reúne todos os alertas de desmatamento no território brasileiro e os cruza com informações relevantes como autorizações, embargos, números de registro de propriedades, áreas protegidas, terras indígenas, etc.

Você pode encontrar informações sobre o projeto [aqui](http://alerta.mapbiomas.org/en?cama_set_language=en).

## 🚀 Servidor Local

Este projeto inclui um servidor local FastAPI que atua como wrapper RESTful para a API GraphQL do MapBiomas Alert.

### Como executar o servidor

#### Opção 1: Script Batch (Windows)
```bash
# Execute o arquivo .bat
run_server.bat
```

#### Opção 2: Script Python (Multiplataforma)
```bash
# Execute o script Python
python run_server.py
```

#### Opção 3: Manual
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
cd src
uvicorn mapbiomas_api_server:app --reload --host 0.0.0.0 --port 8000
```

### Acessar o servidor
- **API Base URL**: http://localhost:8000
- **Documentação Interativa**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc

### Endpoints disponíveis
- `POST /token` - Autenticação
- `GET /alerts` - Buscar alertas paginados
- `GET /alerts/all` - Buscar todos os alertas
- `GET /alert/{alertCode}` - Buscar alerta específico
- `GET /alerts/report` - Relatório detalhado de alerta
- `GET /territories/options` - Opções de territórios
- `GET /alerts/from-car/{carCode}` - Alertas por código CAR
- `GET /alerts/{alertCode}/actions` - Ações por alerta

### How to install
```
git clone https://github.com/Gui-Luz/mapbiomas-alert-api
```

### How to use
##### Importing the package:

```python3
from src.map_biomas_api import MapBiomasAlertApi
```
##### Authenticating
```python3
credentials = {'email': 'your email',
               'password': 'your password'}
token = MapBiomasAlertApi.token(credentials)
```
##### Quering the service
After getting your bearer token you can use the api to query the service. 

Currently, MapBiomas offers seven types of queries:
- Published Alerts
- Published Alert
- Alert Report
- Territories
- Alerts From Car
- Alert Actions
- Territories of Interest

You can find the complete service documentation [here](https://plataforma.alerta.mapbiomas.org/api/documentation).

To query the service, you should use the query function of the MapBiomasAlertApi object passing your token, the query and filters as arguments.

##### Example
In the example bellow we query published alerts by date
```python3
filters = {
  "startDetectedAt": "2020-01-01",
  "endDetectedAt": "2021-12-30",
  "startPublishedAt": "2020-01-01",
  "endPublishedAt": "2021-12-30",
  "offset": 0,
  "limit": 2
}
result = MapBiomasAlertApi.query(token,
                                 MapBiomasAlertApi.PUBLISHED_ALERTS_QUERY,
                                 filters)

```

In the example bellow we query published alert by alert code
```python
filters = {
  "alertCode": "14691"
}
result = MapBiomasAlertApi.query(token,
                                 MapBiomasAlertApi.PUBLISHED_ALERT_QUERY,
                                 filters)
```
The result object of the query above should be a dictionary containing the information about the deforastion alert
```python3
{
  "data": {
    "publishedAlert": {
      "alertCode": "14691",
      "areaHa": 1.2429,
      "sources": [
        "DETERB-AMAZONIA"
      ],
      "bbox": [
        -56.3378933695091,
        -6.0042908703269475,
        -56.320931339719536,
        -5.9873288405373835
      ],
      "alertBiomes": [
        "AMAZÔNIA"
      ],
      "alertCities": [
        "ITAITUBA"
      ],
      "alertStates": [
        "PARÁ"
      ],
      "detectedAt": "2019-06-04",
      "publishedAt": "2020-02-11",
      "deforestationClass": null
    }
  }
}
```