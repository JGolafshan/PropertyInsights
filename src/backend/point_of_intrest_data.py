#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import asyncio
import time
import logging
import overpy

POI_CATEGORIES = {
    "school": ("amenity", "school"),
    "hospital": ("amenity", "hospital"),
    "park": ("leisure", "park"),
    "train_station": ("railway", "station"),
    "tram_stop": ("railway", "tram_stop"),
    "bus_stop": ("highway", "bus_stop"),
    "supermarket": ("shop", "supermarket"),
    "shopping_centre": ("shop", "mall"),
    "cafe": ("amenity", "cafe"),
    "restaurant": ("amenity", "restaurant"),
    "gym": ("leisure", "fitness_centre"),
    "pharmacy": ("amenity", "pharmacy"),
    "police": ("amenity", "police"),
    "fire_station": ("amenity", "fire_station"),
}

log = logging.getLogger(__name__)

_overpass_api = overpy.Overpass()

_POI_CACHE: dict[tuple, tuple[float, list[dict]]] = {}
_CACHE_TTL_SECONDS = 300.0
_MAX_CACHE_SIZE = 100

_LAST_REQUEST_TS = 0.0
_MIN_SECONDS_BETWEEN_REQUESTS = 1.2
_REQ_LOCK = asyncio.Lock()


def _cache_key_from_bbox(south: float, west: float, north: float, east: float, selected_pois: list[str]) -> tuple:
    bbox_key = (round(south, 2), round(west, 2), round(north, 2), round(east, 2))
    pois_key = tuple(sorted(selected_pois or []))
    return bbox_key + (pois_key,)


def build_overpass_query_bbox(south: float, west: float, north: float, east: float, selected_pois: list[str]) -> str:
    blocks = []

    for poi in selected_pois:
        if poi in POI_CATEGORIES:
            key, value = POI_CATEGORIES[poi]
            if value:
                blocks.append(f'nwr({south},{west},{north},{east})["{key}"="{value}"];')
            else:
                blocks.append(f'nwr({south},{west},{north},{east})["{key}"];')

    if not blocks:
        return ""

    return f"""
    [out:json][timeout:25];
    (
      {''.join(blocks)}
    );
    out center;
    """


def _infer_category(tags: dict) -> str | None:
    if not tags:
        return None
    for category, (k, v) in POI_CATEGORIES.items():
        if k in tags and (v is None or str(tags.get(k)) == str(v)):
            return category
    return None


def _poi_from_overpy_element(el) -> dict | None:
    """
    Convert overpy Node/Way/Relation to {lat, lon, name, category, ...}
    Requires `out center;` in the query for ways/relations.
    """
    tags = getattr(el, "tags", None) or {}
    name = tags.get("name")

    osm_type = el.__class__.__name__.lower()  # "node" / "way" / "relation"
    osm_id = getattr(el, "id", None)

    lat = None
    lon = None

    # Node has direct lat/lon
    if hasattr(el, "lat") and hasattr(el, "lon"):
        try:
            lat = float(el.lat)
            lon = float(el.lon)
        except Exception:
            lat = None
            lon = None

    # Way/Relation may have center_lat/center_lon when using `out center;`
    if (lat is None or lon is None) and hasattr(el, "center_lat") and hasattr(el, "center_lon"):
        try:
            lat = float(el.center_lat)
            lon = float(el.center_lon)
        except Exception:
            lat = None
            lon = None

    if lat is None or lon is None:
        return None

    return {
        "id": osm_id,
        "osm_type": osm_type,
        "lat": lat,
        "lon": lon,
        "name": name,
        "tags": tags,
        "category": _infer_category(tags),
    }


def _query_overpass_sync(query_text: str) -> list[dict]:
    """
    Blocking Overpass call (overpy is sync). We'll run this in a thread.
    """
    result = _overpass_api.query(query_text)

    pois: list[dict] = []

    for n in getattr(result, "nodes", []) or []:
        poi = _poi_from_overpy_element(n)
        if poi:
            pois.append(poi)

    for w in getattr(result, "ways", []) or []:
        poi = _poi_from_overpy_element(w)
        if poi:
            pois.append(poi)

    for r in getattr(result, "relations", []) or []:
        poi = _poi_from_overpy_element(r)
        if poi:
            pois.append(poi)

    return pois


async def get_pois_in_bbox_async(
    *,
    south: float,
    west: float,
    north: float,
    east: float,
    selected_pois: list[str],
    use_cache: bool = True,
    retries: int = 2,
) -> list[dict]:
    key = _cache_key_from_bbox(south, west, north, east, selected_pois)
    now = time.time()

    if use_cache and key in _POI_CACHE:
        ts, data = _POI_CACHE[key]
        if now - ts <= _CACHE_TTL_SECONDS:
            return data

    query_text = build_overpass_query_bbox(south, west, north, east, selected_pois)
    if not query_text:
        return []

    for attempt in range(retries + 1):
        try:
            async with _REQ_LOCK:
                global _LAST_REQUEST_TS
                now2 = time.time()
                wait = _MIN_SECONDS_BETWEEN_REQUESTS - (now2 - _LAST_REQUEST_TS)
                if wait > 0:
                    await asyncio.sleep(wait)
                _LAST_REQUEST_TS = time.time()

                # Run blocking overpy query in a worker thread
                pois = await asyncio.to_thread(_query_overpass_sync, query_text)

            if use_cache:
                if len(_POI_CACHE) >= _MAX_CACHE_SIZE:
                    oldest_key = min(_POI_CACHE.keys(), key=lambda k: _POI_CACHE[k][0])
                    del _POI_CACHE[oldest_key]
                _POI_CACHE[key] = (time.time(), pois)

            return pois

        except Exception as e:
            log.warning("Overpass (overpy) query failed (attempt %d/%d): %s", attempt + 1, retries + 1, e)
            if attempt < retries:
                await asyncio.sleep(0.8 * (attempt + 1))
                continue
            break

    if use_cache and key in _POI_CACHE:
        return _POI_CACHE[key][1]
    return []