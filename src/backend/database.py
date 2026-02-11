#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 02/07/2025
Author: Joshua David Golafshan
"""

import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from src.backend.property_db_model import PropertyDocument
from src.backend.application_constants import DB_PASSWORD, DB_APP_NAME, DB_NAME, DB_USERNAME


MONGODB_URI = (
    f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@"
    f"{DB_NAME}/"
    f"?retryWrites=true&w=majority&appName={DB_APP_NAME}"
)

DATABASE_NAME = "property_insights"


async def init_db():
    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[PropertyDocument],
    )

async def insert_property(property_data):
    try:
        doc = PropertyDocument(**property_data.model_dump())
        await doc.insert()
    except DuplicateKeyError:
        pass


async def get_all_properties(limit: int = 100, only_with_geo: bool = True):
    """
    Get properties from database.

    Args:
        limit: Maximum number of properties to return
        only_with_geo: If True, only return properties with valid coordinates

    Returns:
        List of PropertyDocument instances
    """
    query = {}
    if only_with_geo:
        query = {
            "address.latitude": {"$exists": True, "$ne": None},
            "address.longitude": {"$exists": True, "$ne": None}
        }

    return await PropertyDocument.find(query).limit(limit).to_list()

def _build_attribute_elem_match(attribute_name: str, min_count: int) -> dict:
    return {
        "attributes": {
            "$elemMatch": {
                "attribute_name": attribute_name,
                "attribute_count": {"$gte": int(min_count)},
            }
        }
    }


async def get_filtered_properties(
    *,
    price_min: int | None = None,
    price_max: int | None = None,
    property_types: list[str] | None = None,
    min_bedrooms: int | None = None,
    min_bathrooms: int | None = None,
    limit: int = 300,
):
    """
    Filter properties using MongoDB for structural filters, and do a small amount of
    Python-side filtering for price (because your price model can represent:
    actual, range, from, or None).
    """

    query_parts: list[dict] = []

    if property_types:
        # Assumes DB stores values like "House", "Apartment", etc.
        query_parts.append({"property_type": {"$in": property_types}})

    if min_bedrooms is not None:
        query_parts.append(_build_attribute_elem_match("bedrooms", min_bedrooms))

    if min_bathrooms is not None:
        query_parts.append(_build_attribute_elem_match("bathrooms", min_bathrooms))

    mongo_query = {"$and": query_parts} if query_parts else {}

    # Fetch candidates from DB first
    candidates = await PropertyDocument.find(mongo_query).limit(limit).to_list()

    # Price filtering (Python-side)
    if price_min is None and price_max is None:
        return candidates

    def price_passes(p: PropertyDocument) -> bool:
        if not p.price:
            return False

        # Interpret the stored price into an interval [lo, hi]
        lo = None
        hi = None

        if p.price.actual_price and p.price.actual_price > 0:
            lo = hi = float(p.price.actual_price)
        else:
            # guide values
            lo = float(p.price.min_price_guide) if p.price.min_price_guide is not None and p.price.min_price_guide > 0 else 0.0
            # if max guide is 0 for "from", treat as open-ended
            if p.price.max_price_guide and p.price.max_price_guide > 0:
                hi = float(p.price.max_price_guide)
            else:
                hi = float("inf")

        if price_min is not None and hi < float(price_min):
            return False
        if price_max is not None and lo > float(price_max):
            return False
        return True

    return [p for p in candidates if price_passes(p)]


async def get_total_property_count() -> int:
    """
    Total number of Property documents in the database.
    """
    return await PropertyDocument.find_all().count()