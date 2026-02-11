#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 04/02/2025
Author: Joshua David Golafshan
"""

import asyncio
import threading
from concurrent.futures import Future
import math


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def format_price(price):
    if not price:
        return "N/A"

    actual = price.actual_price
    min_price = price.min_price_guide
    max_price = price.max_price_guide

    if actual and actual > 0:
        return f"${actual:,.0f}"
    elif min_price and max_price:
        return f"${min_price:,.0f} - ${max_price:,.0f}"
    elif min_price:
        return f"From ${min_price:,.0f}"
    else:
        return "N/A"


def has_valid_geo(p) -> bool:
    """
    True if property has an address with usable latitude/longitude.
    Works with both Pydantic/Beanie models used in this project.
    """
    if not p or not getattr(p, "address", None):
        return False

    lat = getattr(p.address, "latitude", None)
    lon = getattr(p.address, "longitude", None)

    if lat is None or lon is None:
        return False

    try:
        float(lat)
        float(lon)
    except (TypeError, ValueError):
        return False

    return True


class _AsyncRunner:
    """
    Runs an asyncio event loop in a dedicated background thread.
    This avoids 'Future attached to a different loop' errors with Motor/Beanie
    when Dash callbacks run in different threads.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._loop_ready = threading.Event()
        self._thread = threading.Thread(target=self._thread_main, daemon=True)
        self._thread.start()
        self._loop_ready.wait()

    def _thread_main(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        self._loop_ready.set()
        loop.run_forever()

    @classmethod
    def instance(cls) -> "_AsyncRunner":
        with cls._lock:
            if cls._instance is None:
                cls._instance = _AsyncRunner()
            return cls._instance

    def run(self, coro):
        cf: Future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return cf.result()


def run_async(coro):
    """
    Run an async coroutine from sync code (Dash callbacks, startup code).
    Ensures all coroutines execute on the same event loop.
    """
    return _AsyncRunner.instance().run(coro)