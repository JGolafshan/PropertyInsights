#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 09/08/2025
Author: Joshua David Golafshan
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from configparser import ConfigParser

# Determine project root relative to this file
SCRIPT_DIR = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_DIR.parents[2]

# Create mandatory files
folder_list = [
    "storage",
    "storage/logs",
    "storage/images",
    "storage/data",
]

for folder in folder_list:
    folder_path = PROJECT_ROOT / folder
    folder_path.mkdir(parents=True, exist_ok=True)

# Load config.ini
config = ConfigParser()
config_folder_path = os.path.join(Path(__file__).resolve().parents[2], "config")
config.read(os.path.join(config_folder_path, "config.ini"))


# === Helper to get from config.ini or fallback to .env ===
def get_config_var(key, section="application_settings", default=None, required=False):
    val = os.getenv(key)  # .env has priority
    if not val and config.has_option(section, key):
        val = config.get(section, key)
    if required and not val:
        raise EnvironmentError(f"Missing required configuration: {key}")
    return val or default

# === Core Paths ===
ENV_PATH = PROJECT_ROOT / ".env"
LOGGING_LEVEL = get_config_var("LOG_LEVEL", default="INFO")
LOGGING_LOCATION = os.path.join(PROJECT_ROOT, "storage", "logs")
raw_save_location = get_config_var("SAVE_LOCATION", default="DEFAULT")

if raw_save_location.strip().upper() == "DEFAULT":
    SAVE_LOCATION = PROJECT_ROOT / "storage" / "data"
else:
    SAVE_LOCATION = Path(raw_save_location).expanduser().resolve()

# Load .env file
load_dotenv(ENV_PATH)
