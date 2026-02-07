#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

from dash import html, dcc


def Navbar():
    return html.Nav(
        className="navbar",
        children=[

            # Left: Brand
            html.Div(
                "Property Insights",
                className="navbar-brand"
            ),

            # Center: Search
            html.Div(
                className="navbar-search",
                children=[
                    html.Div(
                        className="search-wrapper",
                        children=[
                            html.I(className="fas fa-search search-icon"),

                            dcc.Input(
                                id="property-search",
                                type="text",
                                placeholder="Search suburb, postcode",
                                className="search-input",
                            ),

                            html.Div(
                                id="search-dropdown",
                                className="search-dropdown",
                                children=[
                                    html.Div("Sydney NSW", className="search-option"),
                                    html.Div("Melbourne VIC", className="search-option"),
                                ],
                            ),
                        ],
                    )
                ],
            ),

            # Right: Icons
            html.Div(
                className="navbar-links",
                children=[
                    html.I(className="fas fa-cog icon", id="filter-modal-open"),
                    html.I(className="fas fa-layer-group icon", id="poi-modal-open"),
                    html.I(className="fas fa-road icon", id="ed-modal-open"),
                ],
            ),
        ],
    )
