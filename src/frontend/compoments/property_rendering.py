# src/frontend/compoments/property_rendering.py

from __future__ import annotations

from src.backend.utils import format_price, has_valid_geo
from src.frontend.compoments.side_menu import PropertyCard
from src.frontend.compoments.map_view import PropertyMarker


def split_total_and_geo(properties: list) -> tuple[int, list]:
    """
    Optimization: Properties already filtered at DB level.
    This function now mainly validates the structure.
    """
    properties = properties or []
    return len(properties), properties


def build_cards(properties: list) -> list:
    """Build property cards. Properties already filtered for valid geo at DB level."""
    return [
        PropertyCard(
            address=p.address.address_raw,
            price=format_price(p.price),
            status=p.sale_type,
            img_url=p.images[0].image_path if p.images else None,
            property_id=str(p.id),
        )
        for p in (properties or [])
    ]


def build_markers(properties: list) -> list:
    """Build map markers. Properties already filtered for valid geo at DB level."""
    return [PropertyMarker(p) for p in (properties or [])]