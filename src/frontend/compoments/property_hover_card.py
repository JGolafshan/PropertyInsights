#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

from __future__ import annotations

from dash import html
from src.backend.property_db_model import PropertyDocument
from src.backend.utils import format_price
from src.backend.application_constants import PROJECT_ROOT


def _attr_map(p: PropertyDocument) -> dict[str, int]:
    """
    Convert p.attributes -> {name: count}
    Handles missing/None attributes safely.
    """
    out: dict[str, int] = {}
    for a in (getattr(p, "attributes", None) or []):
        name = getattr(a, "attribute_name", None)
        count = getattr(a, "attribute_count", None)
        if not name:
            continue
        try:
            out[str(name).strip().lower()] = int(count)
        except (TypeError, ValueError):
            continue
    return out


def _get_land_size_display(p: PropertyDocument) -> str | None:
    """
    Land size isn't in the current Pydantic model, but it may exist in DB documents
    depending on how the scraper stored it. Try common names and return a display string.
    """
    for key in ("land_size", "landSizeDisplay", "land_size_display", "landSize", "land_size_m2"):
        val = getattr(p, key, None)
        if val is None:
            continue
        s = str(val).strip()
        if s and s.lower() != "n/a":
            return s
    return None


def _feature_item(icon_class: str, text: str):
    return html.Div(
        className="popup-feature",
        children=[
            html.I(className=f"{icon_class} popup-feature-icon"),
            html.Span(text, className="popup-feature-text"),
        ],
    )


def PropertyHoverCard(p: PropertyDocument):
    img_src = (
        p.images[0].image_path
        if getattr(p, "images", None) and len(p.images) > 0 and getattr(p.images[0], "image_path", None)
        else PROJECT_ROOT + "/assets/placeholder.jpg"
    )

    address = (
        p.address.address_raw
        if getattr(p, "address", None) and getattr(p.address, "address_raw", None)
        else "Address unavailable"
    )

    price_txt = format_price(getattr(p, "price", None))

    attrs = _attr_map(p)
    beds = attrs.get("bedrooms")
    baths = attrs.get("bathrooms")
    cars = attrs.get("car_spaces") or attrs.get("carspaces") or attrs.get("car space")
    land = _get_land_size_display(p)

    features = []
    if beds is not None:
        features.append(_feature_item("fas fa-bed", f"{beds} bed"))
    if baths is not None:
        features.append(_feature_item("fas fa-bath", f"{baths} bath"))
    if cars is not None:
        features.append(_feature_item("fas fa-car", f"{cars} car"))
    if land is not None:
        features.append(_feature_item("fas fa-ruler-combined", str(land)))

    return html.Div(
        className="popup-card",
        children=[
            html.Div(
                className="popup-image-wrapper",
                children=html.Img(
                    src=img_src,
                    className="popup-image",
                ),
            ),
            html.Div(
                className="popup-content",
                children=[
                    html.H3(address, className="popup-title"),
                    html.P(price_txt, className="popup-price"),
                    html.Div(
                        className="popup-features",
                        children=features,
                    ) if features else None,
                    html.A(
                        ["View details", html.I(className="fas fa-arrow-up-right-from-square popup-cta-icon")],
                        href=getattr(p, "url", None) or "#",
                        target="_blank",
                        className="popup-button",
                        **({"aria-disabled": "true"} if not getattr(p, "url", None) else {}),
                    ),
                ],
            ),
        ],
    )