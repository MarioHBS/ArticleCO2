mutation = \
    """mutation($email: String!, $password: String!)
        { 
        signIn(email: $email, password: $password)
            {
                token
            }
        }
    """

territories_query = \
    """
    query
    (
        $category: TerritoryCategoryEnum
    )
    {
    territories
    (
        category: $category
    )
        {
            id
            name
        }
    }
    """

published_alerts_query = """
query getAlerts(
  $startDate: BaseDate
  $endDate: BaseDate
  $page: Int
  $limit: Int
  $territoryIds: [Int!]
) {
  alerts(
    startDate:    $startDate
    endDate:      $endDate
    page:         $page
    limit:        $limit
    territoryIds: $territoryIds
  ) {
    collection {
      alertCode
      areaHa
      detectedAt
      crossedCitiesList   # nomes das cidades cruzadas
      geometryWkt         # geometria em WKT
      sources             # fontes do alerta
    }
    metadata {
      totalCount
      totalPages
      currentPage
      limitValue
    }
  }
}
"""

published_alert_query = \
    """
    query published_alert($alertCode: String!) {
      publishedAlert(alertCode: $alertCode) {
        alertCode
        areaHa
        sources
        bbox
        alertBiomes
        alertCities
        alertStates
        detectedAt
        publishedAt
        deforestationClass
      }
    }
    """


alert_report_query = \
    """
    query
    (
      $alertCode: Int!
      $carId: Int
    )
    {
      alertReport(alertCode: $alertCode, carId: $carId) {
        alertAreaInCar
        alertCode
        alertGeomWkt
        areaHa
        carCode
        changes {
          labels
        #   layer
          overYears {
            imageUrl
            year
          }
        }
        # imageGridMeasurements {
        #   latitude {
            # startCoordinate
            # endCoordinate
            # steps {
            #   step
            #   stepCoordinate
            # }
        #   }
        #   longitude {
            # startCoordinate
            # endCoordinate
            # steps {
            #   step
            #   stepCoordinate
            # }
        #   }
        # }
        images {
          before {
            acquiredAt
            satellite
            url
          }
          after {
            acquiredAt
            satellite
            url
          }
        #   labels
          alertInProperty
          propertyInState
        }
        intersections {
          conservationUnits {
            area
            # count
          }
          deforestmentsAuthorized {
            area
            # count
          }
          forestManagements {
            area
            # count
          }
          indigenousLands {
            area
            # count
          }
          settlements {
            area
            # count
          }
          withRuralProperty {
            embargoes {
              area
            #   count
            }
            legalReserves {
              area
            #   count
            }
            permanentProtected {
              area
            #   count
            }
            riverSources {
            #   area
              count
            }
          }
        }
        simplifiedPoints {
          imageUrl
          table {
            number
            x
            y
          }
        }
        source
        territories {
          categoryName
          id
          name
        }
        # warnings
      }
    }
    """

alerts_from_car_query = \
    """
    query alert_from_car($carCode:String!) {
      alertsFromCar(carCode:$carCode) 
    }
    """

actions_by_alert_query = \
    """
    query actions_by_alert($alertCode: Int!) {
      actionsByAlert(alertCode: $alertCode){
        actionDate
        actionType
        description
        ruralPropertyId
        link
      }
    }
    """

territories_of_interest_query = \
    """
    query my_maps{
      myMaps{
       alertNotifications {
       alert{
           alertCode
           alertInsertedAt
           bbox
         }
       }
       name
       territories {
         name
         version
       }
     }
    }
    """
