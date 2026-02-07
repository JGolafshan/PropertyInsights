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

class PropertyHistory(BaseModel):
    """Historical or current listing information for a property."""
    is_current: bool = True
    price: float
    url: str
    sale_type: str
    price_range: str
    property_type: str
    images: Optional[List[Images]] = Field(default_factory=list)
    features: Optional[List[PropertyFeatures]] = Field(default_factory=list)
    attributes: Optional[List[PropertyAttributes]] = Field(default_factory=list)

class Property(BaseModel):
    """Represents a property with location and listing history."""
    address: str
    longitude: float
    latitude: float
    history_arr: Optional[List[PropertyHistory]] = Field(default_factory=list)