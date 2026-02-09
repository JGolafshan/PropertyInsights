#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 02/07/2025
Author: Joshua David Golafshan
"""

import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from src.backend.property_db_model import PropertyDocument
from src.backend.application_constants import DB_PASSWORD, DB_APP_NAME, DB_NAME, DB_USERNAME


MONGODB_URI = (
    f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}"
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


async def test_property():
    await init_db()

    property_doc = PropertyDocument(
        address="123 Bondi Rd, Sydney",
        longitude=151.2767,
        latitude=-33.8910,
        history_arr=[
            {
                "is_current": True,
                "price": 1500000,
                "url": "https://example.com/listing/123",
                "sale_type": "sale",
                "price_range": "1.5M-1.6M",
                "property_type": "house",
                "images": [{"image_path": "/images/house1.jpg", "is_primary": True}],
                "features": [{"feature_name": "Pool"}],
                "attributes": [{"attribute_name": "Bedroom", "attribute_count": 3}],
            }
        ]
    )

    # Insert
    await property_doc.insert()
    print(f"Inserted property with id: {property_doc.id}")

    # Query
    found = await PropertyDocument.get(property_doc.id)
    print(f"Found property at: {found.address} with price: {found.history_arr[0].price}")

if __name__ == "__main__":
    asyncio.run(test_property())
