#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import dash_bootstrap_components as dbc
from dash import Output, Input, State
from dash import html, dcc
from dash.exceptions import PreventUpdate

from src.backend.database import get_filtered_properties, get_all_properties, get_total_property_count
from src.backend.utils import run_async
from src.frontend.compoments.side_menu import PropertyCard
from src.backend.utils import format_price
from src.frontend.compoments.map_view import PropertyMarker


DEFAULT_PRICE_RANGE = [200000, 1500000]
DEFAULT_PROPERTY_TYPES = None
DEFAULT_MIN_BEDROOMS = None
DEFAULT_MIN_BATHROOMS = None


def FilterModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Filters")),

            dbc.ModalBody(
                [
                    # Price Range
                    html.Div(
                        [
                            html.Label("Price Range ($)"),
                            dcc.RangeSlider(
                                id="filter-price-range",
                                min=100000,
                                max=5000000,
                                step=50000,
                                marks={
                                    100000: "$100k",
                                    500000: "$500k",
                                    1000000: "$1M",
                                    2500000: "$2.5M",
                                    5000000: "$5M",
                                },
                                tooltip={"placement": "bottom", "always_visible": False},
                                value=DEFAULT_PRICE_RANGE,
                            ),
                        ],
                        style={"margin-bottom": "20px"},
                    ),

                    # Property Type
                    html.Div(
                        [
                            html.Label("Property Type"),
                            dcc.Dropdown(
                                id="filter-property-type",
                                options=[
                                    {"label": "House", "value": "House"},
                                    {"label": "Apartment", "value": "Apartment"},
                                    {"label": "Townhouse", "value": "Townhouse"},
                                    {"label": "Land", "value": "Land"},
                                ],
                                multi=True,
                                placeholder="Select property type(s)",
                                value=DEFAULT_PROPERTY_TYPES,
                            ),
                        ],
                        style={"margin-bottom": "20px"},
                    ),

                    # Attributes: Bedrooms, Bathrooms, etc.
                    html.Div(
                        [
                            html.Label("Bedrooms"),
                            dcc.Input(
                                id="filter-bedrooms",
                                type="number",
                                min=0,
                                step=1,
                                placeholder="Min bedrooms",
                                style={"width": "100px"},
                                value=DEFAULT_MIN_BEDROOMS,
                            ),
                        ],
                        style={"margin-bottom": "10px"},
                    ),

                    html.Div(
                        [
                            html.Label("Bathrooms"),
                            dcc.Input(
                                id="filter-bathrooms",
                                type="number",
                                min=0,
                                step=1,
                                placeholder="Min bathrooms",
                                style={"width": "100px"},
                                value=DEFAULT_MIN_BATHROOMS,
                            ),
                        ],
                        style={"margin-bottom": "10px"},
                    ),
                ]
            ),

            dbc.ModalFooter(
                [
                    dbc.Button("Reset", id="filter-reset", color="secondary", className="me-auto"),
                    dbc.Button("Apply Filters", id="filter-apply", color="primary", className="me-2"),
                    dbc.Button("Close", id="filter-modal-close", color="secondary"),
                ]
            ),
        ],
        id="filter-modal",
        className="filter-modal",
        is_open=False,
        backdrop=True,
        centered=True,
        size="lg",
    )


def register_filter_modal(app):
    @app.callback(
        Output("filter-modal", "is_open"),
        Input("filter-modal-open-desktop", "n_clicks"),
        Input("filter-modal-open-mobile", "n_clicks"),
        Input("filter-modal-close", "n_clicks"),
        State("filter-modal", "is_open"),
    )
    def toggle_filter_modal(_open_desktop, _open_mobile, close, is_open):
        if _open_desktop or _open_mobile or close:
            return not is_open
        return is_open

    @app.callback(
        Output("property-list", "children"),
        Output("property-markers", "children"),
        Output("property-count-label", "children", allow_duplicate=True),
        Output("filter-modal", "is_open", allow_duplicate=True),
        Input("filter-apply", "n_clicks"),
        State("filter-price-range", "value"),
        State("filter-property-type", "value"),
        State("filter-bedrooms", "value"),
        State("filter-bathrooms", "value"),
        prevent_initial_call=True,
    )
    def apply_filters(n_clicks, price_range, property_types, min_bedrooms, min_bathrooms):
        if not n_clicks:
            raise PreventUpdate

        price_min, price_max = (None, None)
        if isinstance(price_range, (list, tuple)) and len(price_range) == 2:
            price_min, price_max = int(price_range[0]), int(price_range[1])

        props = run_async(
            get_filtered_properties(
                price_min=price_min,
                price_max=price_max,
                property_types=property_types or None,
                min_bedrooms=min_bedrooms,
                min_bathrooms=min_bathrooms,
                limit=400,
            )
        )

        cards = [
            PropertyCard(
                address=p.address.address_raw,
                price=format_price(p.price),
                status=p.sale_type,
                img_url=p.images[0].image_path if p.images else None,
                property_id=str(p.id),
            )
            for p in props
            if p and p.address
        ]

        markers = [PropertyMarker(p) for p in props if p and p.address]

        total_count = run_async(get_total_property_count())
        count_label = f"Showing {len(props or []):,} of {int(total_count or 0):,}"

        return cards, markers, count_label, False

    @app.callback(
        Output("filter-price-range", "value"),
        Output("filter-property-type", "value"),
        Output("filter-bedrooms", "value"),
        Output("filter-bathrooms", "value"),
        Output("property-list", "children", allow_duplicate=True),
        Output("property-markers", "children", allow_duplicate=True),
        Output("property-count-label", "children", allow_duplicate=True),
        Input("filter-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(n_clicks):
        if not n_clicks:
            raise PreventUpdate

        props = run_async(get_all_properties(limit=400))

        cards = [
            PropertyCard(
                address=p.address.address_raw,
                price=format_price(p.price),
                status=p.sale_type,
                img_url=p.images[0].image_path if p.images else None,
                property_id=str(p.id),
            )
            for p in props
            if p and p.address
        ]

        markers = [PropertyMarker(p) for p in props if p and p.address]

        total_count = run_async(get_total_property_count())
        count_label = f"Showing {len(props or []):,} of {int(total_count or 0):,}"

        return (
            DEFAULT_PRICE_RANGE,
            DEFAULT_PROPERTY_TYPES,
            DEFAULT_MIN_BEDROOMS,
            DEFAULT_MIN_BATHROOMS,
            cards,
            markers,
            count_label,
        )