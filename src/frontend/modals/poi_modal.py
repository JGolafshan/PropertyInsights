#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import dash_bootstrap_components as dbc
from dash import Output, Input, State


def PointOfIntrestModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Point of Interest")),
            dbc.ModalBody("Filter content here"),
            dbc.ModalFooter(
                dbc.Button("Close", id="poi-modal-close")
            ),
        ],
        id="poi-modal",
        is_open=False,
    )

def register_poi_modal(app):
    @app.callback(
        Output("poi-modal", "is_open"),
        Input("poi-modal-open", "n_clicks"),
        Input("poi-modal-close", "n_clicks"),
        State("poi-modal", "is_open"),
    )
    def toggle_search_modal(open, close, is_open):
        if open or close:
            return not is_open
        return is_open
