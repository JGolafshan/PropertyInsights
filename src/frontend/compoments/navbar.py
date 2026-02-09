#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import pandas as pd
from dash import html, dcc
from dash.exceptions import PreventUpdate
from dash import Input, Output, State, ALL
from src.backend.application_constants import SAVE_LOCATION

POSTCODES_DF = pd.read_csv(SAVE_LOCATION / "au_postcodes.csv", dtype={"postcode": str})

# Create a display label once
POSTCODES_DF["label"] = (POSTCODES_DF["place_name"] + ", " + POSTCODES_DF["state_code"] + " " + POSTCODES_DF["postcode"])

def Navbar():
    return html.Nav(
        className="navbar",
        children=[

            # Left: Brand
            html.Div(
                "Property Insights",
                className="navbar-brand"
            ),

            # Center: Search
            html.Div(
                className="navbar-search",
                children=[
                    html.Div(
                        className="search-wrapper",
                        children=[
                            html.I(className="fas fa-search search-icon"),

                            dcc.Input(
                                id="property-search",
                                type="text",
                                placeholder="Search suburb, postcode",
                                className="search-input",
                            ),

                            html.Div(
                                id="search-dropdown",
                                className="search-dropdown",
                                children=[
                                    html.Div("Sydney NSW", className="search-option"),
                                    html.Div("Melbourne VIC", className="search-option"),
                                ],
                            ),
                        ],
                    )
                ],
            ),

            # Right: Icons
            html.Div(
                className="navbar-links",
                children=[
                    html.I(className="fas fa-cog icon", id="filter-modal-open"),
                    html.I(className="fas fa-layer-group icon", id="poi-modal-open"),
                    html.I(className="fas fa-road icon", id="ed-modal-open"),
                ],
            ),
        ],
    )

def register_search_callbacks(app):

    @app.callback(
        Output("search-dropdown", "children"),
        Output("search-dropdown", "style"),
        Input("property-search", "value"),
    )
    def update_search_dropdown(search_value):

        if not search_value or len(search_value) < 2:
            return [], {"display": "none"}

        search_value = search_value.lower()

        matches = POSTCODES_DF[
            POSTCODES_DF["label"].str.lower().str.contains(search_value)
        ].head(8)

        options = [
            html.Div(
                row["label"],
                className="search-option",
                id={"type": "search-option", "index": i},
                **{
                    "data-lat": row["latitude"],
                    "data-lon": row["longitude"],
                }
            )
            for i, row in matches.iterrows()
        ]

        return options, {"display": "block"}

    @app.callback(
        Output("property-search", "value"),
        Output("search-dropdown", "style", allow_duplicate=True),
        Output("selected-location", "data"),
        Input({"type": "search-option", "index": ALL}, "n_clicks"),
        State({"type": "search-option", "index": ALL}, "children"),
        State({"type": "search-option", "index": ALL}, "data-lat"),
        State({"type": "search-option", "index": ALL}, "data-lon"),
        prevent_initial_call=True,
    )
    def select_location(n_clicks, labels, lats, lons):

        if not n_clicks:
            raise PreventUpdate

        safe_clicks = [c or 0 for c in n_clicks]

        if max(safe_clicks) == 0:
            raise PreventUpdate

        idx = safe_clicks.index(max(safe_clicks))

        return (
            labels[idx],
            {"display": "none"},
            {
                "label": labels[idx],
                "lat": float(lats[idx]),
                "lon": float(lons[idx]),
            }
        )
