#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import pandas as pd
from dash import html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import Input, Output, State, ALL
from dash import html, dcc, Output, Input, State

from src.backend.application_constants import SAVE_LOCATION


def SearchModal():
    return dbc.Modal(
        [
            dbc.ModalBody(
                dbc.Container(
                    [
                        dcc.Input(
                            id="expandable-search-input",
                            type="text",
                            placeholder="Search suburbs or postcodes…",
                            className="expandable-search-input",
                            debounce=True,
                        ),

                        html.Div(
                            id="expandable-search-dropdown",
                            className="expandable-search-dropdown",
                        ),
                    ],
                    className="search-modal-content",
                ),
            ),
        ],
        id="search-modal",
        is_open=False,
        backdrop=True,     # click-off works
        centered=True,
        size="xl",
        className="search-modal",
    )

POSTCODES_DF = pd.read_csv(SAVE_LOCATION / "au_postcodes.csv", dtype={"postcode": str})

# Create a display label once
POSTCODES_DF["label"] = (POSTCODES_DF["place_name"] + ", " + POSTCODES_DF["state_code"] + " " + POSTCODES_DF["postcode"])

def register_search_modal_callbacks(app):
    @app.callback(
        Output("expandable-search-dropdown", "children"),
        Output("expandable-search-dropdown", "style"),
        Input("expandable-search-input", "value"),
    )
    def update_modal_search(search_value):

        if not search_value or len(search_value) < 2:
            return [], {"display": "none"}

        search_value = search_value.lower()

        matches = POSTCODES_DF[
            POSTCODES_DF["label"].str.lower().str.contains(search_value)
        ].head(10)

        options = [
            html.Div(
                row["label"],
                className="search-option",
                id={"type": "modal-search-option", "index": i},
                **{
                    "data-lat": row["latitude"],
                    "data-lon": row["longitude"],
                }
            )
            for i, row in matches.iterrows()
        ]

        return options, {"display": "block"}

    @app.callback(
        Output("expandable-search-input", "value"),
        Output("expandable-search-dropdown", "style", allow_duplicate=True),
        Output("selected-location", "data", allow_duplicate=True),
        Output("search-modal", "is_open", allow_duplicate=True),
        Input({"type": "modal-search-option", "index": ALL}, "n_clicks"),
        State({"type": "modal-search-option", "index": ALL}, "children"),
        State({"type": "modal-search-option", "index": ALL}, "data-lat"),
        State({"type": "modal-search-option", "index": ALL}, "data-lon"),
        prevent_initial_call=True,
    )
    def select_modal_location(n_clicks, labels, lats, lons):

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
            },
            False,  # close modal
        )

def register_search_modal_toggle(app):
    @app.callback(
        Output("search-modal", "is_open", allow_duplicate=True),
        Input("search-modal-open", "n_clicks"),
        State("search-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_search_modal(n, is_open):
        return not is_open

