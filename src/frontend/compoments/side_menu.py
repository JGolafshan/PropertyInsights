#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

from dash import html
from src.backend.application_constants import PROJECT_ROOT
from src.backend.utils import format_price, has_valid_geo
from dash import Input, Output, State, ALL, ctx
from dash.exceptions import PreventUpdate

# --- new helpers (kept local so sidebar cards can reuse them) ---
def _attr_map(p) -> dict[str, int]:
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


def _get_land_size_display(p) -> str | None:
    for key in ("land_size", "landSizeDisplay", "land_size_display", "landSize", "land_size_m2"):
        val = getattr(p, key, None)
        if val is None:
            continue
        s = str(val).strip()
        if s and s.lower() != "n/a":
            return s
    return None


def _feature_chip(icon_class: str, text: str):
    return html.Span(
        className="property-meta-chip",
        children=[
            html.I(className=f"{icon_class}"),
            html.Span(text),
        ],
    )


def PropertyCard(
    address,
    price,
    status,
    img_url=None,
    property_id=None,
    beds: int | None = None,
    baths: int | None = None,
    cars: int | None = None,
    land: str | None = None,
):
    meta = []
    if beds is not None:
        meta.append(_feature_chip("fas fa-bed", f"{beds}"))
    if baths is not None:
        meta.append(_feature_chip("fas fa-bath", f"{baths}"))
    if cars is not None:
        meta.append(_feature_chip("fas fa-car", f"{cars}"))
    if land:
        meta.append(_feature_chip("fas fa-ruler-combined", str(land)))

    return html.Div(
        className="property-card horizontal",
        id={"type": "property-card", "id": property_id},
        n_clicks=0,
        children=[
            # Image on the left
            html.Img(
                src=img_url or PROJECT_ROOT + "/assets/placeholder.jpg",
                className="property-thumbnail",
            ),
            # Text content on the right
            html.Div(
                className="property-info",
                children=[
                    html.Div(
                        [
                            html.Div(address, className="property-address"),
                        ],
                        className="property-header",
                    ),
                    html.Div(
                        className="property_supplemental",
                        children=[
                            html.Div(price, className="property-price"),
                            html.Span(status, className=f"property-status {status.lower().replace(' ', '-')}")
                        ]
                    ),
                    html.Div(className="property-meta", children=meta) if meta else None,
                ],
            ),
        ],
    )


def _count_label_text(shown_count: int, total_count: int) -> str:
    try:
        shown = int(shown_count or 0)
        total = int(total_count or 0)
    except (TypeError, ValueError):
        shown, total = 0, 0
    return f"Showing {shown:,} of {total:,}"


def PropertyMenu(*, total_count: int = 0, shown_count: int = 0):
    return html.Div(
        id="property-selector",
        children=[
            html.Div(
                className="sidebar-header",
                children=[
                    html.Div(
                        className="sidebar-header-left",
                        children=[
                            html.H4("Property List", className="sidebar-title"),
                            html.Div(
                                id="property-count-label",
                                className="sidebar-count",
                                children=_count_label_text(shown_count, total_count),
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.I(className="fas fa-search icon", id="search-modal-open-desktop"),
                            html.I(className="fas fa-cog icon", id="filter-modal-open-desktop"),
                            html.I(className="fas fa-layer-group icon", id="poi-modal-open-desktop"),
                            html.I(className="fas fa-road icon", id="ed-modal-open-desktop"),
                        ],
                        id="options-list",
                    ),
                ],
            ),
            html.Hr(),
        ],
    )


def PropertyCards(properties):
    # Optimization: properties are already filtered for geo at DB level
    # No need to re-filter with has_valid_geo
    return html.Div(
        id="property-list",
        children=[
            PropertyCard(
                address=listing.address.address_raw,
                price=format_price(listing.price),
                status=listing.sale_type,
                img_url=listing.images[0].image_path if listing.images else None,
                property_id=str(listing.id),
                beds=_attr_map(listing).get("bedrooms"),
                baths=_attr_map(listing).get("bathrooms"),
                cars=_attr_map(listing).get("car_spaces")
                     or _attr_map(listing).get("carspaces")
                     or _attr_map(listing).get("car space"),
                land=_get_land_size_display(listing),
            )
            for listing in (properties or [])
        ],
    )




def register_property_card_callbacks(app, properties):
    # Optimization: index properties by id for O(1) lookup instead of O(n) search
    # Properties already filtered for geo at DB level
    property_lookup = {str(p.id): p for p in (properties or [])}

    @app.callback(
        Output("selected-location", "data", allow_duplicate=True),
        Input({"type": "property-card", "id": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_property(_n_clicks_list):
        if not ctx.triggered_id:
            raise PreventUpdate

        property_id = ctx.triggered_id["id"]
        prop = property_lookup.get(property_id)

        if not has_valid_geo(prop):
            raise PreventUpdate

        return {
            "lat": float(prop.address.latitude),
            "lon": float(prop.address.longitude),
        }