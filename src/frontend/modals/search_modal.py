#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import Input, Output, State, ALL
from dash import html, dcc

from src.frontend.compoments.location_search import (
    build_option_divs,
    search_postcodes,
)


def SearchModal():
    return dbc.Modal(
        [
            dbc.ModalBody(
                dbc.Container(
                    [
                        html.Div(
                            className="search-wrapper search-wrapper--modal",
                            children=[
                                html.I(className="fas fa-search search-icon search-icon--modal"),
                                dcc.Input(
                                    id="expandable-search-input",
                                    type="text",
                                    placeholder="Search suburbs or postcodes…",
                                    className="expandable-search-input",
                                    debounce=False,
                                    autoComplete="off",
                                ),
                                html.Button(
                                    html.I(className="fas fa-xmark"),
                                    id="expandable-search-clear",
                                    className="search-clear-btn search-clear-btn--modal",
                                    n_clicks=0,
                                    type="button",
                                    style={"display": "none"},
                                ),
                            ],
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
        backdrop=True,  # click-off works
        centered=True,
        size="xl",
        className="search-modal",
    )


def register_search_modal_callbacks(app):
    @app.callback(
        Output("expandable-search-dropdown", "children"),
        Output("expandable-search-dropdown", "style"),
        Input("expandable-search-input", "value"),
    )
    def update_modal_search(search_value):
        if not search_value or len(search_value) < 2:
            return [], {"display": "none"}

        matches = search_postcodes(search_value, limit=10)
        options = build_option_divs(matches, option_type="modal-search-option")

        return options, {"display": "block"}

    @app.callback(
        Output("expandable-search-clear", "style"),
        Input("expandable-search-input", "value"),
    )
    def toggle_modal_clear_button(value):
        if value:
            return {"display": "flex"}
        return {"display": "none"}

    @app.callback(
        Output("expandable-search-input", "value", allow_duplicate=True),
        Output("expandable-search-dropdown", "style", allow_duplicate=True),
        Input("expandable-search-clear", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_modal_search(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return "", {"display": "none"}

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
        Input("search-modal-open-desktop", "n_clicks"),
        Input("search-modal-open-mobile", "n_clicks"),
        State("search-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_search_modal(_n1, _n2, is_open):
        return not is_open