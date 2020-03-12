from json import JSONDecodeError
from requests import get, RequestException
from flask import Blueprint, request, current_app
from .models import Station, db
import json

bp = Blueprint('api_v1', __name__, url_prefix='/api/v1/metro')


@bp.route("/verificate", methods=['POST'])
def compairer():
    try:
        deserialized_data = json.loads(request.data)
    except JSONDecodeError as err:
        return f"Can't deserialize object: {err}", 400
    stations_from_api = get_station(current_app.config["METRO_STATION_URL"])
    output = {"unchanged": None, "updated": None, "deleted": None}
    input_data_set = set(deserialized_data)
    from_db_data_set = set()
    for line in stations_from_api["lines"]:
        for station in line["stations"]:
            station["metro_id"] = station["id"]
            del station["id"]
            _, _ = add_if_not_exist(**station)
            from_db_data_set.add(station["name"])
    output["unchanged"] = list(input_data_set & from_db_data_set)
    output["updated"] = list(input_data_set - from_db_data_set)
    output["deleted"] = list(from_db_data_set - input_data_set)
    return output


# тестами не покрыто
def get_station(link):
    try:
        r = get(link)
    except RequestException as err:
        return err
    try:
        deserialized_data = r.json()
    except ValueError as err:
        return err
    return deserialized_data


# тестами не покрыто
def add_if_not_exist(**kwargs):
    instance = db.session.query(Station).filter_by(metro_id=kwargs["metro_id"]).first()
    if not instance:
        instance = Station(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance, True
    for k, v in kwargs.items():
        if getattr(instance, k) is not v:
            setattr(instance, k, v)
    db.session.commit()
    return instance, False
