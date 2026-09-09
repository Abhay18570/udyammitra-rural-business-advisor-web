"""Shared PostGIS geography expressions; distances are spheroidal metres."""
from geoalchemy2 import Geography
from sqlalchemy import cast, func


def geography_point(latitude, longitude):
    return cast(func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326), Geography(geometry_type="POINT", srid=4326))


def distance_meters(point, origin):
    return func.ST_Distance(point, origin)


def within_meters(point, origin, radius):
    return func.ST_DWithin(point, origin, radius)
