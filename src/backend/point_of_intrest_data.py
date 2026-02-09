#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import overpy

POI_CATEGORIES = {
    # Education
    "childcare": ("amenity", "childcare"),
    "kindergarten": ("amenity", "kindergarten"),
    "school": ("amenity", "school"),
    "college": ("amenity", "college"),
    "university": ("amenity", "university"),

    # Health
    "hospital": ("amenity", "hospital"),
    "clinic": ("amenity", "clinic"),
    "doctors": ("amenity", "doctors"),
    "dentist": ("amenity", "dentist"),
    "pharmacy": ("amenity", "pharmacy"),
    "aged_care": ("amenity", "nursing_home"),

    # Transport
    "train_station": ("railway", "station"),
    "tram_stop": ("railway", "tram_stop"),
    "bus_stop": ("highway", "bus_stop"),
    "parking": ("amenity", "parking"),

    # Retail
    "supermarket": ("shop", "supermarket"),
    "convenience": ("shop", "convenience"),
    "bakery": ("shop", "bakery"),
    "butcher": ("shop", "butcher"),
    "greengrocer": ("shop", "greengrocer"),
    "shopping_centre": ("shop", "mall"),

    # Food
    "cafe": ("amenity", "cafe"),
    "restaurant": ("amenity", "restaurant"),
    "fast_food": ("amenity", "fast_food"),
    "bar": ("amenity", "bar"),
    "pub": ("amenity", "pub"),

    # Recreation
    "park": ("leisure", "park"),
    "playground": ("leisure", "playground"),
    "sports_centre": ("leisure", "sports_centre"),
    "gym": ("leisure", "fitness_centre"),
    "swimming_pool": ("leisure", "swimming_pool"),
    "beach": ("natural", "beach"),

    # Civic
    "police": ("amenity", "police"),
    "fire_station": ("amenity", "fire_station"),
    "post_office": ("amenity", "post_office"),
    "library": ("amenity", "library"),

    # Employment
    "office": ("office", None),
    "industrial": ("landuse", "industrial"),
    "commercial": ("landuse", "commercial"),
    "bank": ("amenity", "bank"),
    "atm": ("amenity", "atm"),
}



api = overpy.Overpass()


def build_overpass_query(lat, lon, radius, selected_pois):
    blocks = []

    for poi in selected_pois:
        if poi in POI_CATEGORIES:
            key, value = POI_CATEGORIES[poi]
            if value:
                blocks.append(
                    f'node(around:{radius},{lat},{lon})["{key}"="{value}"];'
                )
            else:
                blocks.append(
                    f'node(around:{radius},{lat},{lon})["{key}"];'
                )

    return f"""
    (
      {''.join(blocks)}
    );
    out body;
    """


def get_pois(lat: float, lon: float, radius: int, selected_pois: list[str]):
    query = build_overpass_query(
        lat=lat,
        lon=lon,
        radius=radius,
        selected_pois=selected_pois
    )

    result = api.query(query)

    pois = []

    for node in result.nodes:
        pois.append({
            "id": node.id,
            "lat": node.lat,
            "lon": node.lon,
            "name": node.tags.get("name"),
            "tags": node.tags,
        })

    return pois





LAT = -33.8688     # Sydney CBD
LON = 151.2093
RADIUS = 1500      # metres

selected_pois = [
    "school",
    "hospital",
    "train_station",
    "supermarket",
    "park",
    "cafe",
]

pois = get_pois(
    lat=LAT,
    lon=LON,
    radius=RADIUS,
    selected_pois=selected_pois
)

print(f"Found {len(pois)} POIs")
print(pois[:3])
