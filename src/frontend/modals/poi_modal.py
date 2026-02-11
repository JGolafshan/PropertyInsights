#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

from dash import html
from dash import Output, Input, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from src.backend.point_of_intrest_data import POI_CATEGORIES


def PointOfInterestModal():
    options = [
        {"label": key.replace("_", " ").title(), "value": key}
        for key in POI_CATEGORIES.keys()
    ]

    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Points of Interest", className="poi-modal-title"),
            ),
            dbc.ModalBody(
                html.Div(
                    [
                        dbc.Checklist(
                            id="poi-selected",
                            options=options,
                            value=[],
                            inline=False,
                            className="poi-modal-body",
                        )
                    ]
                )
            ),
            dbc.ModalFooter(
                children=[
                    dbc.Button("Reset", id="poi-reset", className="me-auto poi-close-btn", color="secondary"),
                    dbc.Button("Apply", id="poi-apply", className="poi-close-btn", color="primary"),
                    dbc.Button("Close", id="poi-modal-close", className="poi-close-btn", color="secondary"),
                ]
            ),
        ],
        id="poi-modal",
        is_open=False,
        centered=True,
        size="lg",
        className="poi-modal",
    )


def register_poi_modal(app):
    @app.callback(
        Output("poi-modal", "is_open"),
        Input("poi-modal-open-desktop", "n_clicks"),
        Input("poi-modal-open-mobile", "n_clicks"),
        Input("poi-modal-close", "n_clicks"),
        State("poi-modal", "is_open"),
    )
    def toggle_poi_modal(_open_desktop, _open_mobile, close_clicks, is_open):
        if _open_desktop or _open_mobile or close_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("poi-selected", "value"),
        Output("selected-pois", "data"),
        Input("poi-selected", "value"),
        Input("poi-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def sync_selected_pois(selected, reset_clicks):
        if reset_clicks:
            return [], []

        if selected is None:
            raise PreventUpdate

        return selected, selected

    @app.callback(
        Output("poi-apply", "children"),
        Input("poi-apply", "n_clicks"),
        prevent_initial_call=True,
    )
    def _probe_apply_click(n):
        return f"Apply ({n})"