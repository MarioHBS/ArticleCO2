from fastapi import FastAPI, HTTPException, Depends, Header, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os

from map_biomas_api import MapBiomasAlertApi

app = FastAPI(
    title="MapBiomas Alert API V2 Wrapper",
    version="1.0.0",
    description="RESTful wrapper around the MapBiomas GraphQL Alert API V2"
)

# ----- Models -----


class AuthCredentials(BaseModel):
    email: str
    password: str


class AlertsParams(BaseModel):
    startDate: str
    endDate: str
    page: int = 1
    limit: int = 100
    territoryIds: Optional[List[int]] = None

# ----- Dependencies -----


def get_token(authorization: str = Header(None)) -> str:
    # 1) tenta extrair do header
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    # 2) fallback para MAPBIOMIAS_TOKEN
    token_env = os.getenv("MAPBIOMIAS_TOKEN")
    if token_env:
        return token_env
    raise HTTPException(401, "Missing or invalid Authorization header")

# ----- Endpoints -----


@app.post("/token")
def login(creds: AuthCredentials) -> Dict[str, str]:
    """
    Perform GraphQL signIn mutation to get a new token.
    """
    try:
        token = MapBiomasAlertApi.token(creds.dict())
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/alerts")
def get_alerts(
        startDate: str = Query(..., description="YYYY-MM-DD"),
        endDate:   str = Query(..., description="YYYY-MM-DD"),
        page:      int = Query(1, ge=1),
        limit:     int = Query(100, ge=1, le=1000),
        territoryIds: Optional[str] = Query(
            None, description="Comma-separated list of territory IDs"),
        token: str = Depends(get_token)
) -> Any:
    """
    Fetch paginated alerts. territoryIds is optional comma-separated list.
    """
    vars: Dict[str, Any] = {"startDate": startDate,
                            "endDate": endDate, "page": page, "limit": limit}
    if territoryIds:
        try:
            vars["territoryIds"] = [int(x) for x in territoryIds.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid territoryIds format")

    try:
        resp = MapBiomasAlertApi.query(
            token, MapBiomasAlertApi.PUBLISHED_ALERTS_QUERY, vars)
        return resp["data"]["alerts"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts/all")
def get_all_alerts(
        startDate: str = Query(..., description="YYYY-MM-DD"),
        endDate:   str = Query(..., description="YYYY-MM-DD"),
        territoryIds: Optional[str] = Query(
            None, description="Comma-separated list of territory IDs"),
        token: str = Depends(get_token)
) -> Any:
    """
    Fetch all alerts across all pages for given parameters.
    """
    # Prepare variables with large limit
    vars: Dict[str, Any] = {"startDate": startDate,
                            "endDate": endDate, "page": 1, "limit": 1000}
    if territoryIds:
        try:
            vars["territoryIds"] = [int(x) for x in territoryIds.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid territoryIds format")
    # First request to get metadata
    resp = MapBiomasAlertApi.query(
        token, MapBiomasAlertApi.PUBLISHED_ALERTS_QUERY, vars)
    alerts_data = resp["data"]["alerts"]
    all_collection = alerts_data["collection"]
    total_pages = alerts_data["metadata"]["totalPages"]

    # Loop through remaining pages
    for page in range(2, total_pages + 1):
        vars["page"] = page
        resp = MapBiomasAlertApi.query(
            token, MapBiomasAlertApi.PUBLISHED_ALERTS_QUERY, vars)
        all_collection.extend(resp["data"]["alerts"]["collection"])

    return {"collection": all_collection}


@app.get("/alert/{alertCode}")
def get_alert(alertCode: str, token: str = Depends(get_token)) -> Any:
    """
    Fetch a single published alert by its code.
    """
    try:
        resp = MapBiomasAlertApi.query(
            token, MapBiomasAlertApi.PUBLISHED_ALERT_QUERY, {"alertCode": alertCode})
        return resp["data"]["publishedAlert"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts/report")
def get_alert_report(
        alertCode: int = Query(...),
        carId: Optional[int] = Query(None),
        token: str = Depends(get_token)
) -> Any:
    """
    Fetch detailed report for an alert, optionally within a CAR.
    """
    vars = {"alertCode": alertCode}
    if carId is not None:
        vars["carId"] = carId
    try:
        resp = MapBiomasAlertApi.query(
            token, MapBiomasAlertApi.ALERT_REPORT_QUERY, vars)
        return resp["data"]["alertReport"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/territories/options")
def list_territory_options(token: str = Depends(get_token)) -> Any:
    """
    List all territoryOption categories and their entries.
    """
    query = """
    query {
      territoryOptions {
        categoryName
        territories { code name }
      }
    }
    """
    try:
        resp = MapBiomasAlertApi.query(token, query, {})
        return resp["data"]["territoryOptions"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts/from-car/{carCode}")
def get_alerts_from_car(carCode: str, token: str = Depends(get_token)) -> Any:
    """
    List alert codes for a given CAR code.
    """
    try:
        resp = MapBiomasAlertApi.query(
            token, MapBiomasAlertApi.ALERTS_FROM_CAR_QUERY, {"carCode": carCode})
        return resp["data"]["alertsFromCar"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts/{alertCode}/actions")
def get_actions_by_alert(alertCode: int, token: str = Depends(get_token)) -> Any:
    """
    List actions associated with an alert code.
    """
    try:
        resp = MapBiomasAlertApi.query(
            token, MapBiomasAlertApi.ACTIONS_BY_ALERT_QUERY, {"alertCode": alertCode})
        return resp["data"]["actionsByAlert"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
