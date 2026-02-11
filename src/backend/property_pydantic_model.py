#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 02/07/2025
Author: Joshua David Golafshan
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Images(BaseModel):
    """Represents a property image."""
    image_path: str
    is_primary: bool = False

class PropertyFeatures(BaseModel):
    """Represents a feature of the property."""
    feature_name: str

class PropertyAttributes(BaseModel):
    """Represents a counted attribute of the property (e.g. bedrooms)."""
    attribute_name: str
    attribute_count: int

class PropertyAddress(BaseModel):
    """Represents a property address."""
    address_raw: str
    longitude: float
    latitude: float

class PropertyPrice(BaseModel):
    """Represents a price of the property."""
    actual_price: float
    min_price_guide: float
    max_price_guide: float

class Property(BaseModel):
    """Represents a property"""
    url: str
    sale_type: str
    property_type: str
    land_size: Optional[str]
    address: Optional[PropertyAddress]
    price: Optional[PropertyPrice] = None
    images: Optional[List[Images]] = Field(default_factory=list)
    features: Optional[List[PropertyFeatures]] = Field(default_factory=list)
    attributes: Optional[List[PropertyAttributes]] = Field(default_factory=list)
