#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""
import logging

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from src.backend.database import get_all_properties, init_db, get_total_property_count
from src.backend.utils import run_async, has_valid_geo
from src.frontend.compoments.navbar import Navbar, register_search_callbacks
from src.frontend.compoments.map_view import MapView, register_map_callbacks
from src.frontend.compoments.side_menu import PropertyMenu, PropertyCards, register_property_card_callbacks
from src.frontend.modals.filter_modal import register_filter_modal, FilterModal
from src.frontend.modals.poi_modal import register_poi_modal, PointOfInterestModal
from src.frontend.modals.external_data_modal import register_ed_modal, ExternalDataModal
from src.frontend.modals.search_modal import SearchModal, register_search_modal_callbacks, register_search_modal_toggle


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logging.getLogger("aio_overpass").setLevel(logging.INFO)


run_async(init_db())

db_total_count = run_async(get_total_property_count())

data = run_async(get_all_properties(only_with_geo=True))
shown_count = len(data or [])


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
        dcc.Store(id="selected-location"),
        dcc.Store(id="selected-pois", data=[]),
        dcc.Store(id="poi-data", data=[]),
        dcc.Store(id="selected-dimension-points", data=[]),

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
                        PropertyMenu(total_count=db_total_count, shown_count=shown_count),
                        PropertyCards(properties=data),
                    ],
                ),
                # Map (full width on mobile, reduced on desktop)
                html.Div(
                    MapView(properties=data),
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
register_filter_modal(app)
register_poi_modal(app)
register_ed_modal(app)
register_search_callbacks(app)
register_property_card_callbacks(app, data)

if __name__ == "__main__":
    app.run(debug=True)
