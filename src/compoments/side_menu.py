#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Date: 04/02/2025
    Author: Joshua David Golafshan
"""

from dash import html


def PropertyCard(address, price, status, img_url=None):
    return html.Div(
        className="property-card horizontal",
        children=[
            # Image on the left
            html.Img(
                src=img_url or "/assets/placeholder.jpg",
                className="property-thumb",
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
                            html.I(className="fas fa-cog icon"),
                            html.I(className="fas fa-layer-group icon"),
                            html.I(className="fas fa-road icon")
                        ],
                        id="filter-button",
                        title="Open Filters",
                        n_clicks=0,
                    ),
                ],
            )
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