#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import dash_leaflet as dl
from dash import Input, Output, State, ctx, html, dcc
from dash.exceptions import PreventUpdate
from src.backend.property_db_model import PropertyDocument
from src.backend.utils import run_async
from src.frontend.compoments.property_hover_card import property_hover_card
from src.backend.point_of_intrest_data import get_pois_in_bbox_async

# (Color, Name, Icon)
POI_STYLE = {
    "school": ("#2563eb", "School", "fa-solid fa-graduation-cap"),
    "hospital": ("#dc2626", "Hospital", "fa-solid fa-hospital"),
    "park": ("#16a34a", "Park", "fa-solid fa-tree"),
    "train_station": ("#111827", "Train", "fa-solid fa-train"),
    "tram_stop": ("#111827", "Tram", "fa-solid fa-train-tram"),
    "bus_stop": ("#111827", "Bus", "fa-solid fa-bus"),
    "supermarket": ("#7c3aed", "Supermarket", "fa-solid fa-cart-shopping"),
    "shopping_centre": ("#7c3aed", "Shopping", "fa-solid fa-bag-shopping"),
    "cafe": ("#b45309", "Cafe", "fa-solid fa-mug-saucer"),
    "restaurant": ("#b45309", "Restaurant", "fa-solid fa-utensils"),
    "gym": ("#0f766e", "Gym", "fa-solid fa-dumbbell"),
    "pharmacy": ("#db2777", "Pharmacy", "fa-solid fa-pills"),
    "police": ("#1f2937", "Police", "fa-solid fa-shield-halved"),
    "fire_station": ("#ef4444", "Fire", "fa-solid fa-fire-extinguisher"),
}

# (Color, Icon)
PROPERTY_STYLE = {
    "house": ("#2563eb", "fa-solid fa-house"),
    "apartment": ("#2563eb","fa-solid fa-building"),
    "land": ("#2563eb", "fa-solid fa-mound"),
    "other": ("#2563eb", "fa-solid fa-sign-hanging"),
}


def property_marker(p: PropertyDocument):
    prop_type = p.property_type.lower()
    default_set = PROPERTY_STYLE.get("other")
    color, icon_cls = PROPERTY_STYLE.get(prop_type, default_set)

    name = p.address.address_raw

    icon = dict(
        html=f"""
        <div class="poi-fa-bubble" title="{name}" style="border:2px solid {color}; color:{color};">
            <i class="{icon_cls}"></i>
        </div>
        """,
        className="poi-fa-icon",
        iconSize=[26, 26],
        iconAnchor=[13, 13],
    )

    return dl.DivMarker(
        position=[p.address.latitude, p.address.longitude],
        iconOptions=icon,
        children=[
            dl.Popup(
                property_hover_card(p),
                autoClose=True,
                closeOnEscapeKey=True,
                closeButton=False,
                maxWidth=320,
                className="property-popup",
            )
        ],
    )

def poi_marker(poi: dict):
    poi_type = poi.get("category")
    color, label, icon_cls = POI_STYLE.get(
        poi_type, ("#111827", "POI", "fa-solid fa-location-dot")
    )

    name = poi.get("name") or label

    icon = dict(
        html=f"""
        <div class="poi-fa-bubble" title="{name}" style="border:2px solid {color}; color:{color};">
            <i class="{icon_cls}"></i>
        </div>
        """,
        className="poi-fa-icon",
        iconSize=[26, 26],
        iconAnchor=[13, 13],
    )

    return dl.DivMarker(
        position=[float(poi["lat"]), float(poi["lon"])],
        iconOptions=icon,
    )


def map_view(properties):
    return html.Div(
        style={"width": "100%", "height": "100%"},
        children=[
            dcc.Store(id="map-resize-done"),

            dcc.Interval(id="map-resize-kick", interval=300, n_intervals=0, max_intervals=1),
            dl.Map(
                children=[
                    dl.TileLayer(url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"),

                    dl.MeasureControl(
                        position="topleft",
                        primaryLengthUnit="kilometers",
                        secondaryLengthUnit="meters",
                        primaryAreaUnit="hectares",
                        activeColor="#2563eb",
                        completedColor="#16a34a",
                    ),

                    dl.LayerGroup(id="property-markers", children=[property_marker(p) for p in properties]),
                    dl.LayerGroup(id="poi-markers", children=[]),
                ],
                center=[-33.8688, 151.2093],
                zoom=10,
                zoomControl=False,
                style={"width": "100%", "height": "100%"},
                preferCanvas=True,
                id="main_map",
            ),
        ],
    )


def register_map_callbacks(app):
    app.clientside_callback(
        """
        function(n) {
            if (!n) {
                return window.dash_clientside.no_update;
            }
            window.dispatchEvent(new Event('resize'));
            return Date.now();
        }
        """,
        Output("map-resize-done", "data"),
        Input("map-resize-kick", "n_intervals"),
    )

    @app.callback(
        Output("main_map", "viewport"),
        Input("selected-location", "data"),
    )
    def move_map(location):
        if not location:
            raise PreventUpdate

        lat = location.get("lat")
        lon = location.get("lon")

        if lat is None or lon is None:
            raise PreventUpdate

        return {
            "center": [lat, lon],
            "zoom": 14,
            "transition": "flyTo",
        }

    @app.callback(
        Output("poi-markers", "children"),
        Input("poi-data", "data"),
    )
    def render_pois(poi_data):
        if not poi_data:
            return []
        return [poi_marker(p) for p in poi_data]

    @app.callback(
        Output("poi-data", "data"),
        Input("poi-apply", "n_clicks"),
        Input("poi-reset", "n_clicks"),
        State("main_map", "bounds"),
        State("main_map", "center"),
        State("selected-pois", "data"),
        prevent_initial_call=True,
    )
    def update_pois(poi_apply_clicks, poi_reset_clicks, bounds, center, selected_pois):
        if ctx.triggered_id == "poi-reset":
            return []

        if not poi_apply_clicks:
            raise PreventUpdate

        if not selected_pois:
            return []

        if not bounds:
            if not center or len(center) != 2:
                raise PreventUpdate
            lat, lon = float(center[0]), float(center[1])
            south, west, north, east = lat - 0.02, lon - 0.02, lat + 0.02, lon + 0.02
        else:
            (sw_lat, sw_lon), (ne_lat, ne_lon) = bounds
            south, west, north, east = float(sw_lat), float(sw_lon), float(ne_lat), float(ne_lon)

        pois = run_async(
            get_pois_in_bbox_async(
                south=south,
                west=west,
                north=north,
                east=east,
                selected_pois=list(selected_pois),
                use_cache=True,
                retries=2,
            )
        )
        return pois