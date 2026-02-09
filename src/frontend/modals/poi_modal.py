#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import dash_bootstrap_components as dbc
from dash import Output, Input, State


from dash import html
import dash_bootstrap_components as dbc

def PointOfInterestModal(poi_list=None):
    if poi_list is None:
        poi_list = [
            "Schools", "Hospitals", "Parks", "Shopping Centers",
            "Transport", "Restaurants", "Gyms", "Cinemas"
        ]

    # Build 2-column rows of POIs
    rows = []
    for i in range(0, len(poi_list), 2):
        col1 = dbc.Col(
            dbc.Checkbox(id=f"poi-{i}", label=poi_list[i], className="poi-checkbox mb-2"),
            width=6
        )
        col2 = dbc.Col(
            dbc.Checkbox(id=f"poi-{i+1}", label=poi_list[i+1], className="poi-checkbox mb-2")
            if i + 1 < len(poi_list) else dbc.Col(width=6),
            width=6
        )
        rows.append(dbc.Row([col1, col2], className="poi-row mb-2 g-3"))

    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Points of Interest", className="poi-modal-title"),
            ),
            dbc.ModalBody(
                html.Div(rows, className="poi-modal-body")
            ),
            dbc.ModalFooter(
                children=[
                    dbc.Button("Reset", id="poi-modal-close", className="ms-auto poi-close-btn"),
                    dbc.Button("Close", id="poi-modal-close", className="ms-auto poi-close-btn"),
                ]
            ),
        ],
        id="poi-modal",
        is_open=False,
        centered=True,
        size="lg",
        className="poi-modal"
    )

def register_poi_modal(app):
    @app.callback(
        Output("poi-modal", "is_open"),
        Input("poi-modal-open", "n_clicks"),
        Input("poi-modal-close", "n_clicks"),
        State("poi-modal", "is_open"),
    )
    def toggle_filter_modal(open, close, is_open):
        if open or close:
            return not is_open
        return is_open
