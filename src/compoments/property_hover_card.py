#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Date: 04/02/2025
    Author: Joshua David Golafshan
"""

from dash import html

def PropertyHoverCard(p):
    return html.Div(
        className="popup-card",
        children=[
            html.Div(
                className="popup-image-wrapper",
                children=html.Img(
                    src=p["img_url"],
                    className="popup-image",
                ),
            ),
            html.Div(
                className="popup-content",
                children=[
                    html.H3(p["address"], className="popup-title"),
                    html.P(p["price_range"], className="popup-price"),

                    html.Div(
                        className="popup-features",
                        children=PropertyAttributes(p),
                    ),

                    html.A(
                        "View Details",
                        href=p.get("url", "#"),
                        target="_blank",
                        className="popup-button",
                    ),
                ],
            ),
        ],
    )

def PropertyAttributes(property):
    attribute_list = []

    if property.get("bedrooms"):
        Feature(
            "https://cdn-icons-png.flaticon.com/512/1946/1946429.png",
            f'{property["bedrooms"]} Beds',
        ),

    if property.get("bathrooms"):
        Feature(
            "https://cdn-icons-png.flaticon.com/512/1946/1946436.png",
            f'{property["bathrooms"]} Baths',
        ),

    if property.get("car_spaces"):
        Feature(
            "https://cdn-icons-png.flaticon.com/512/2972/2972185.png",
            f'{property["car_spaces"]} Car',
        ),
    if property.get("landSizeDisplay"):
        Feature(
            "https://cdn-icons-png.flaticon.com/512/814/814513.png",
            property["landSizeDisplay"],
        )

    return attribute_list

def Feature(icon, text):
    return html.Div(
        className="popup-feature",
        children=[
            html.Img(src=icon),
            html.Span(text),
        ],
    )
