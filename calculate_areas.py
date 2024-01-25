from collections import Counter
from functools import partial
import xml.etree.ElementTree as ET
import warnings

import pyproj
from shapely.geometry.polygon import Polygon
from shapely import ops


warnings.simplefilter("ignore")
kml_prefix = "{http://www.opengis.net/kml/2.2}"

def get_area_of_polygon(polygon):
    geom_area = ops.transform(
        partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(
                proj='aea',
                lat_1=polygon.bounds[1],
                lat_2=polygon.bounds[3]
        )
    ),
    polygon)
    return geom_area.area

def polygon_from_kml_coordinates(coordinates: str)-> list:
    """
    Accept a KML coordinates string
    return a list of tuples suitable for feeding
    shapely.geometry.polygon.Polygon()
    example:
    >>> polygon_from_kml_coordinates("1,2,3 4,5,6")
    [(1, 2), (4, 6)]
    """

    def cleaned(point: str):
        latitude, longitude, _ = point.split(",")
        return tuple([float(latitude), float(longitude)])

    points = coordinates.strip().split(" ")
    return [ cleaned(point) for point in points ]



def kmlize(path: str) -> str:
    return path.replace("/", f"/{kml_prefix}")

def area_format(square_meters: float)-> str:
    square_meters_per_acre = 4046.8564224
    sq_m = round(square_meters)
    acres = round(square_meters / square_meters_per_acre)
    return f"{sq_m:,} m² | {acres:,} acres"

def main():
    types = Counter()
    tree = ET.parse("eugene-downtown-parking.kml")
    doc = tree.getroot()[0]
    park = kmlize("./Placemark") + f"[{kml_prefix}name!='downtown borders']"
    parking = doc.findall(park)
    for item in parking:
        name = item.find(f"{kml_prefix}name").text
        types[name] +=1
    by_quantity = dict(sorted(types.items(), key=lambda el: el[1], reverse=True))
    for k, v in by_quantity.items():
        print(f"{v} {k}")
    print(f"{len(parking)} total parking objects")


    coordinates = kmlize("./Polygon/outerBoundaryIs/LinearRing/coordinates")
    parking_boundaries = [
        place.find(coordinates)
        for place in parking
    ]
    polygons = [
        polygon_from_kml_coordinates(boundary.text)
        for boundary in parking_boundaries
    ]
    polygon_objects = [ Polygon(polygon) for polygon in polygons ]
    areas = [ get_area_of_polygon(polygon) for polygon in polygon_objects ]
    area = sum(areas)
    print(f"{area_format(area)} dedicated to parking")

    dt = kmlize("./Placemark") + f"[{kml_prefix}name='downtown borders']"
    downtown = doc.find(dt)
    dt_boundary = downtown.find(coordinates)
    dt_polygon = Polygon(polygon_from_kml_coordinates(dt_boundary.text))
    dt_area = get_area_of_polygon(dt_polygon)
    print(f"{area_format(dt_area)} in downtown")

    print(f"{round(area / dt_area * 100)}% parking")


main()
