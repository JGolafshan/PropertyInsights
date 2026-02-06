#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Date: 04/02/2025
    Author: Joshua David Golafshan
"""

from dash import html, dcc

def FilterPopup(id_prefix="filter"):
    return html.Div(
        id=f"{id_prefix}-container",
        children=[
            html.Button("Filters", id=f"{id_prefix}-open", className="filter-btn"),

            html.Div(
                id=f"{id_prefix}-modal",
                className="filter-modal",
                children=[
                    html.Div(
                        className="filter-content",
                        children=[
                            html.H4("Filter Properties"),
                            dcc.Dropdown(
                                id=f"{id_prefix}-type",
                                options=[
                                    {"label": "House", "value": "house"},
                                    {"label": "Apartment", "value": "apartment"},
                                ],
                                placeholder="Property Type",
                            ),
                            dcc.RangeSlider(
                                id=f"{id_prefix}-price",
                                min=200_000,
                                max=2_000_000,
                                step=50_000,
                                value=[400_000, 1_200_000],
                                tooltip={"placement": "bottom"}
                            ),
                            html.Button("Close", id=f"{id_prefix}-close")
                        ]
                    )
                ],
                style={"display": "none", "height": "100vh"}
            )
        ]
    )
