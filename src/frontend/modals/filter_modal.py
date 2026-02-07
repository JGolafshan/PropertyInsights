import dash_bootstrap_components as dbc
from dash import Output, Input, State

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""


def FilterModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Filters")),
            dbc.ModalBody("Filter content here"),
            dbc.ModalFooter(
                dbc.Button("Close", id="filter-modal-close")
            ),
        ],
        id="filter-modal",
        is_open=False,
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
