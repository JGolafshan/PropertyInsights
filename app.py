#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

from dash import Dash, html, dcc
from storage.data import test_data
import dash_bootstrap_components as dbc
from src.frontend.compoments.navbar import Navbar, register_search_callbacks
from src.frontend.compoments.map_view import MapView, register_map_callbacks
from src.frontend.compoments.side_menu import PropertyMenu, PropertyCards
from src.frontend.modals.filter_modal import register_filter_modal, FilterModal
from src.frontend.modals.poi_modal import register_poi_modal, PointOfInterestModal
from src.frontend.modals.external_data_modal import register_ed_modal, ExternalDataModal
from src.frontend.modals.search_modal import SearchModal, register_search_modal_callbacks, register_search_modal_toggle

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    ],
)

register_filter_modal(app)
register_poi_modal(app)
register_ed_modal(app)
register_search_callbacks(app)

app.layout = html.Div(
    id="app_container",
    className="container-fluid",
    children=[
        dcc.Store(id="selected-location"),

        FilterModal(),
        PointOfInterestModal(),
        SearchModal(),
        ExternalDataModal(),

        # Mobile Navbar (shown < lg)
        html.Div(
            Navbar(),
            className="d-block d-xl-none"
        ),

        # Main content row
        html.Div(
            className="row g-0",
            children=[

                # Sidebar (desktop only)
                html.Div(
                    className="sidebar col-12 col-xl-3 d-none d-xl-flex flex-column",
                    children=[
                        PropertyMenu(),
                        PropertyCards(properties=test_data),
                    ],
                ),
                # Map (full width on mobile, reduced on desktop)
                html.Div(
                    MapView(properties=test_data),
                    id="property-map",
                    className="col-12 col-xl-9",
                ),
            ],
        ),
    ],
)

register_map_callbacks(app)
register_search_modal_callbacks(app)
register_search_modal_toggle(app)


if __name__ == "__main__":
    app.run(debug=True)
