#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

from dash import html
from src.backend.application_constants import PROJECT_ROOT

def PropertyCard(address, price, status, img_url=None):
    return html.Div(
        className="property-card horizontal",
        children=[
            # Image on the left
            html.Img(
                src=img_url or PROJECT_ROOT + "/assets/placeholder.jpg",
                className="property-thumbnail",
            ),
            # Text content on the right
            html.Div(
                className="property-info",
                children=[
                    html.Div(
                        [
                            html.Div(address, className="property-address"),
                        ],
                        className="property-header",
                    ),
                    html.Div(
                        className="property_supplemental",
                        children=[
                            html.Div(price, className="property-price"),
                            html.Span(status,className=f"property-status {status.lower().replace(' ', '-')}")
                        ]
                    ),
                ],
            ),
        ],
    )

def PropertyMenu():
    return html.Div(
        id="property-selector",
        children=[
            html.Div(
                className="sidebar-header",
                children=[
                    html.H4("Property List", className="sidebar-title"),
                    html.Div(
                        children=[
                            html.I(className="fas fa-search icon", id="search-modal-open"),
                            html.I(className="fas fa-cog icon", id="filter-modal-open"),
                            html.I(className="fas fa-layer-group icon", id="poi-modal-open"),
                            html.I(className="fas fa-road icon", id="ed-modal-open")
                        ],
                        id="options-list",
                    )
                ],
            ),
                html.Hr()
        ]
    )

def PropertyCards(properties):
    return html.Div(
        id="property-list",
        children=[
            PropertyCard(
                address=listing["address"],
                price=listing["price"],
                status=listing["status"],
                img_url=listing["img_url"],
            )
            for listing in properties
        ],
    )