from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from dash import html

from src.backend.application_constants import SAVE_LOCATION


POSTCODES_DF = pd.read_csv(SAVE_LOCATION / "au_postcodes.csv", dtype={"postcode": str})
POSTCODES_DF["label"] = (
    POSTCODES_DF["place_name"] + ", " + POSTCODES_DF["state_code"] + " " + POSTCODES_DF["postcode"]
)


@dataclass(frozen=True)
class Match:
    label: str
    lat: float
    lon: float


def search_postcodes(query: str, *, limit: int) -> list[Match]:
    q = (query or "").strip().lower()
    if len(q) < 2:
        return []

    matches = POSTCODES_DF[POSTCODES_DF["label"].str.lower().str.contains(q)].head(limit)

    out: list[Match] = []
    for _i, row in matches.iterrows():
        out.append(Match(label=row["label"], lat=float(row["latitude"]), lon=float(row["longitude"])))
    return out


def build_option_divs(matches: Iterable[Match], *, option_type: str) -> list[html.Div]:
    options: list[html.Div] = []
    for i, m in enumerate(matches):
        options.append(
            html.Div(
                m.label,
                className="search-option",
                id={"type": option_type, "index": i},
                **{"data-lat": m.lat, "data-lon": m.lon},
            )
        )
    return options