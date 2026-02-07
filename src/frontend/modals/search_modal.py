import dash_bootstrap_components as dbc
from dash import Output, Input, State

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""


def SearchModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Search")),
            dbc.ModalBody("Filter content here"),
            dbc.ModalFooter(
                dbc.Button("Close", id="search-modal-close")
            ),
        ],
        id="search-modal",
        is_open=False,
    )

def register_search_modal(app):
    @app.callback(
        Output("search-modal", "is_open"),
        Input("search-modal-open", "n_clicks"),
        Input("search-modal-close", "n_clicks"),
        State("search-modal", "is_open"),
    )
    def toggle_search_modal(open, close, is_open):
        if open or close:
            return not is_open
        return is_open
