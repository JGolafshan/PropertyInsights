#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

from dash import html, dcc
from dash.exceptions import PreventUpdate
from dash import Input, Output, State, ALL

from src.frontend.compoments.location_search import (
    build_option_divs,
    search_postcodes,
)


def navbar():
    return html.Nav(
        className="navbar",
        children=[
            html.Div("Property Insights", className="navbar-brand"),
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
                                debounce=False,
                                autoComplete="off",
                            ),
                            html.Button(
                                html.I(className="fas fa-xmark"),
                                id="property-search-clear",
                                className="search-clear-btn",
                                n_clicks=0,
                                type="button",
                                style={"display": "none"},
                            ),
                            html.Div(
                                id="search-dropdown",
                                className="search-dropdown",
                                children=[],
                            ),
                        ],
                    )
                ],
            ),
            html.Div(
                className="navbar-links",
                children=[
                    html.I(className="fas fa-magnifying-glass icon none", id="search-modal-open-mobile"),
                    html.I(className="fas fa-cog icon", id="filter-modal-open-mobile"),
                    html.I(className="fas fa-layer-group icon", id="poi-modal-open-mobile"),
                    html.I(className="fas fa-road icon", id="ed-modal-open-mobile"),
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

        matches = search_postcodes(search_value, limit=8)
        options = build_option_divs(matches, option_type="search-option")

        return options, {"display": "block"}

    @app.callback(
        Output("property-search-clear", "style"),
        Input("property-search", "value"),
    )
    def toggle_nav_clear_button(value):
        if value:
            return {"display": "flex"}
        return {"display": "none"}

    @app.callback(
        Output("property-search", "value", allow_duplicate=True),
        Output("search-dropdown", "style", allow_duplicate=True),
        Input("property-search-clear", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_nav_search(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return "", {"display": "none"}

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
            },
        )