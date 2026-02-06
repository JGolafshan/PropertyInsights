#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Date: 04/02/2025
    Author: Joshua David Golafshan
"""

from dash import Dash, html, Output, Input
import dash_bootstrap_components as dbc
from storage.data import test_data
from src.compoments.side_menu import PropertyMenu, PropertyCards
from src.compoments.navbar import Navbar
from src.compoments.map_compoent import MapView

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    ],
)


app.layout = html.Div(
    id="app_container",
    className="container-fluid",
    children=[

        # Mobile Navbar (shown < lg)
        html.Div(
            Navbar(),
            className="d-block d-lg-none"
        ),

        # Main content row
        html.Div(
            className="row g-0",  # g-0 removes unwanted gaps
            children=[

                # Sidebar (desktop only)
                html.Div(
                    className="sidebar col-12 col-xl-2 d-none d-xl-flex flex-column",
                    children=[
                        PropertyMenu(),
                        PropertyCards(properties=test_data),
                    ],
                ),

                # Map (full width on mobile, reduced on desktop)
                html.Div(
                    MapView(properties=test_data),
                    id="property-map",
                    className="col-12 col-xl-10",
                ),
            ],
        ),
    ],
)

@app.callback(
    Output("navbar-links", "className"),
    Input("navbar-toggle", "n_clicks"),
    prevent_initial_call=True
)
def toggle_navbar(n):
    if n % 2 == 1:
        return "navbar-links show"
    return "navbar-links"

if __name__ == "__main__":
    app.run(debug=True)
