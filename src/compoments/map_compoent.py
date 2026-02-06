import dash_leaflet as dl
from src.compoments.property_hover_card import PropertyHoverCard

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Date: 04/02/2025
    Author: Joshua David Golafshan
"""

def PropertyMarker(p):
    return dl.CircleMarker(
        center=[p["lat"], p["lon"]],
        radius=6,
        color="#2563eb",
        fill=True,
        fillOpacity=0.9,
        children=[
            dl.Tooltip(
                PropertyHoverCard(p),
                direction="top",
                opacity=1,
                sticky=True,   # follows cursor slightly
            )
        ],
    )



def MapView(properties):
    return dl.Map(
        children=[
            dl.TileLayer(
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            ),

            dl.LayerGroup(
                [PropertyMarker(p) for p in properties]
            ),
        ],
        center=[-33.8688, 151.2093],
        zoom=12,
        style={"width": "100%", "height": "100%"},
        id="main_map",
    )
