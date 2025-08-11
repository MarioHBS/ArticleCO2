from unittest import TestCase
from src.map_biomas_api import MapBiomasAlertApi


class TestMapBiomasAlertApi(TestCase):

    def setUp(self):
        self.credentials = {
            "email": "<EMAIL>",
            "password": "<PASSWORD>"
        }

    def test_should_return_string_when_trying_to_authenticate_with_right_credentials(self):
        token = MapBiomasAlertApi.token(self.credentials)
        self.assertEqual(type(token), str)

    def test_should_raise_exception_when_trying_to_authenticate_with_wrong_credentials(self):
        wrong_credentials = {
            "email": "abc",
            "password": "123"
        }
        self.assertRaises(Exception, MapBiomasAlertApi.token, wrong_credentials)

    def test_should_return_dict_when_calling_territories_query(self):
        token = MapBiomasAlertApi.token(self.credentials)
        filters = {"category": "INDIGENOUS_LAND"}
        result = MapBiomasAlertApi.query(token, MapBiomasAlertApi.TERRITORIES_QUERY, filters)
        self.assertEqual(type(result), dict)

    def test_should_return_dict_when_calling_alert_report_query(self):
        token = MapBiomasAlertApi.token(self.credentials)
        filters = {'alertCode': 118896}
        result = MapBiomasAlertApi.query(token, MapBiomasAlertApi.ALERT_REPORT_QUERY, filters)
        self.assertEqual(type(result), dict)

    def test_should_return_dict_when_calling_published_alert_query(self):
        token = MapBiomasAlertApi.token(self.credentials)
        filters = {'alertCode': "118896"}
        result = MapBiomasAlertApi.query(token, MapBiomasAlertApi.PUBLISHED_ALERT_QUERY, filters)
        self.assertEqual(type(result), dict)

    def test_should_return_dict_when_calling_published_alerts_query(self):
        token = MapBiomasAlertApi.token(self.credentials)
        filters = {
            "startDetectedAt": "2020-01-01",
            "endDetectedAt": "2021-12-30",
            "startPublishedAt": "2020-01-01",
            "endPublishedAt": "2021-12-30",
            "offset": 0,
            "limit": 10
        }
        result = MapBiomasAlertApi.query(token, MapBiomasAlertApi.PUBLISHED_ALERTS_QUERY, filters)
        self.assertEqual(type(result), dict)

    def test_should_return_dict_when_calling_alerts_from_car_query(self):
        token = MapBiomasAlertApi.token(self.credentials)
        filters = {
            "carCode": "MG-3109303-52977B59C6DC44B193CE795B7E65CE7F"
        }
        result = MapBiomasAlertApi.query(token, MapBiomasAlertApi.ALERTS_FROM_CAR_QUERY, filters)
        self.assertEqual(type(result), dict)

