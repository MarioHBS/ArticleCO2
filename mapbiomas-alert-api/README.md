# MapBiomas Alert Api

### MapBiomas Alert Api is a python client for the MapBiomas Alert Api service.</p>

MapBiomas Alert is a system that validates and refines deforestation alerts with high-resolution images. In one free and open access platform, the service gather all deforestation alerts in Brazil's territory and cross them with relevant information such as authorizations, embargoes, property's registry numbers, protected areas, indigenous lands, etc.

You can find information about the project [here](http://alerta.mapbiomas.org/en?cama_set_language=en).

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