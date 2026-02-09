#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import dash_bootstrap_components as dbc
from dash import Output, Input, State
from dash import html, dcc

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
                                value=[200000, 1500000],
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
                                    {"label": "House", "value": "house"},
                                    {"label": "Apartment", "value": "apartment"},
                                    {"label": "Townhouse", "value": "townhouse"},
                                    {"label": "Land", "value": "land"},
                                ],
                                multi=True,
                                placeholder="Select property type(s)",
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
                            ),
                        ],
                        style={"margin-bottom": "10px"},
                    ),

                    # Additional features (optional multi-select)
                    html.Div(
                        [
                            html.Label("Features"),
                            dcc.Checklist(
                                id="filter-features",
                                options=[
                                    {"label": "Pool", "value": "pool"},
                                    {"label": "Garage", "value": "garage"},
                                    {"label": "Air Conditioning", "value": "ac"},
                                    {"label": "Garden", "value": "garden"},
                                ],
                                inline=True,
                            ),
                        ]
                    ),
                ]
            ),

            dbc.ModalFooter(
                [
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
        Input("filter-modal-open", "n_clicks"),
        Input("filter-modal-close", "n_clicks"),
        State("filter-modal", "is_open"),
    )
    def toggle_filter_modal(open, close, is_open):
        if open or close:
            return not is_open
        return is_open
