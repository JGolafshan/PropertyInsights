import dash_bootstrap_components as dbc
from dash import Output, Input, State

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""


def external_data_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("External Data")),
            dbc.ModalBody("Filter content here"),
            dbc.ModalFooter(
                dbc.Button("Close", id="ed-modal-close")
            ),
        ],
        id="ed-modal",
        is_open=False,
    )

def register_ed_modal(app):
    @app.callback(
        Output("ed-modal", "is_open"),
        Input("ed-modal-open-desktop", "n_clicks"),
        Input("ed-modal-open-mobile", "n_clicks"),
        Input("ed-modal-close", "n_clicks"),
        State("ed-modal", "is_open"),
    )
    def toggle_ed_modal(_open_desktop, _open_mobile, close, is_open):
        if _open_desktop or _open_mobile or close:
            return not is_open
        return is_open