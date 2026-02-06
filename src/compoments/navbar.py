#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Date: 04/02/2025
    Author: Joshua David Golafshan
"""

from dash import html


def Navbar():
    return html.Nav(
        className="navbar",
        children=[
            html.Div("Property Insights", className="navbar-brand"),
            html.Div(
                className="navbar-links",
                children=[
                    html.A("Home", href="#"),
                    html.A("Properties", href="#"),
                    html.A("About", href="#"),
                    html.A("Contact", href="#"),
                ],
            ),
            # Hamburger icon for small screens
            html.Div("☰", className="navbar-toggle", id="navbar-toggle"),
        ],
    )
