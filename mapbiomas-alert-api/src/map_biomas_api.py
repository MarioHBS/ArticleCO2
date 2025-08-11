# -*- coding: utf-8 -*-

import requests
from queries import territories_query, alert_report_query, published_alerts_query, alerts_from_car_query, \
    published_alert_query, actions_by_alert_query, territories_of_interest_query, mutation


class MapBiomasAlertApi(object):
    ENDPOINT = 'https://plataforma.alerta.mapbiomas.org/api/v2/graphql'
    TIMEOUT = 120
    MUTATION_QUERY = mutation
    PUBLISHED_ALERTS_QUERY = published_alerts_query
    PUBLISHED_ALERT_QUERY = published_alert_query
    ALERT_REPORT_QUERY = alert_report_query
    TERRITORIES_QUERY = territories_query
    ALERTS_FROM_CAR_QUERY = alerts_from_car_query
    ACTIONS_BY_ALERT_QUERY = actions_by_alert_query
    TERRITORIES_OF_INTEREST_QUERY = territories_of_interest_query

    @classmethod
    def token(cls, credentials):
        request = requests.post(MapBiomasAlertApi.ENDPOINT, json={'query': cls.MUTATION_QUERY, 'variables': credentials},
                                timeout=MapBiomasAlertApi.TIMEOUT)

        if request.status_code == 200:
            result = request.json()
            if 'errors' in result:
                msg = '\n'.join([error['message']
                                for error in result['errors']])
                raise Exception(msg)
            else:
                return result["data"]["signIn"]["token"]
        else:
            msg = "Failed to run by returning code of {}.".format(
                request.status_code)
            raise Exception(msg)

    @classmethod
    def query(cls, token, query, filters=dict()):

        headers = {'Authorization': 'Bearer ' + token}

        request = requests.post(cls.ENDPOINT, json={'query': query, 'variables': filters}, headers=headers,
                                timeout=cls.TIMEOUT)

        if request.status_code == 200:
            result = request.json()
            if 'errors' in result:
                msg = '\n'.join([error['message']
                                for error in result['errors']])
                raise Exception(msg)
            else:
                return result
        else:
            msg = "Failed to run by returning code of {}.".format(
                request.status_code)
            raise Exception(msg)
