#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 02/07/2025
Author: Joshua David Golafshan
"""

from enum import Enum

class PropertyStatus(Enum):
    ACTIVE = "active"
    SOLD = "sold"
    UNDER_OFFER = "under offer"
    AUCTION = "auction"