#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 02/09/2025
Author: Joshua David Golafshan
"""

import re
import time
import logging
import nodriver as uc
import pandas as pd
from geopy.geocoders import Nominatim
from nodriver.core.element import Element

from src.backend.application_constants import SAVE_LOCATION
from src.backend.property_db_model import PropertyDocument
from src.backend.property_pydantic_model import PropertyHistory

NA_VALUE = "N/A"


class NoDriverScraper:
    def __init__(self, browser: uc.Browser, page: uc.Tab):
        self.browser = browser
        self.page = page
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def wait_for_page(self):
        await self.page.evaluate(
            expression="""
                new Promise((resolve) => {
                    function waitForIdleAfterLoad() {
                        // Use requestIdleCallback if available
                        if ('requestIdleCallback' in window) {
                            requestIdleCallback(() => {
                                setTimeout(resolve, 300);  // small buffer
                            }, {timeout: 3000});
                        } else {
                            // Fallback for older browsers
                            setTimeout(resolve, 500);  // fallback wait
                        }
                    }

                    if (document.readyState === 'complete') {
                        waitForIdleAfterLoad();
                    } else {
                        window.addEventListener('load', waitForIdleAfterLoad);
                    }
                });
            """,
            await_promise=True
        )

    async def get_current_url(self):
        return await self.page.evaluate("window.location.href")

    @staticmethod
    async def highlight_element(element: Element):
        await element.apply(
            """
            el => {
                el.style.setProperty('border', '3px solid red', 'important');
                el.style.padding = '10px';
                el.style.minHeight = '30px';
            }
            """
        )


async def safe_find_async(fn, default=NA_VALUE):
    try:
        return await fn()
    except Exception as e:
        print(f"[safe_find_async] Error: {e}")
        print(f"[function is] Error: {fn.__name__}")
        return default


async def get_text_from(selector, parent):
    element = await parent.query_selector(selector)
    if element:
        return element.text
    return NA_VALUE


async def get_attr_from(selector, attr, parent):
    element = await parent.query_selector(selector)
    if element:
        return element.attrs.get(attr, NA_VALUE)
    return NA_VALUE


async def extract_card_details(card):
    price = await safe_find_async(lambda: get_text_from("span.property-price ", card))
    address = await safe_find_async(lambda: get_text_from("h2.residential-card__address-heading", card))
    image = await safe_find_async(lambda: get_attr_from("div.property-image", "data-url", card))
    url_link = await safe_find_async(lambda: get_attr_from("h2.residential-card__address-heading a", "href", card))

    # make sure it contains the domain
    url_complete = "https://www.realestate.com.au" + url_link

    residential_data = await safe_find_async(lambda: card.query_selector("ul.residential-card__primary"))
    if not residential_data:
        return None

    div_container = await safe_find_async(lambda: residential_data.query_selector("div"))
    if not div_container:
        return None

    room_data = await safe_find_async(lambda: div_container.query_selector_all("li"), [])
    standard_room_types = ["bathroom", "bedroom", "car space", "with study"]
    room_dict = {}

    for room in room_data:
        aria_label = room.attrs.get("aria-label", NA_VALUE)
        if not aria_label:
            continue
        aria_label = aria_label.lower()

        async def get_number_text():
            p = await room.query_selector("p")
            return p.text if p else None

        number_text = await safe_find_async(get_number_text)

        matched_key = None
        for room_type in standard_room_types:
            if room_type in aria_label:
                matched_key = room_type
                break

        if matched_key and number_text and number_text.isdigit():
            room_dict[matched_key] = int(number_text)

    async def get_property_type():
        ps = await residential_data.query_selector_all("p")
        if ps:
            last_p = ps[-1]
            return last_p.text
        return NA_VALUE

    async def get_land_size():
        land_li = await card.query_selector("li[aria-label*='land size'] p")
        return land_li.text if land_li else NA_VALUE

    return {
        "price": price,
        "thumbnail": image,
        "address": address,
        "lat": -1,
        "long": -1,
        "url": url_complete,
        "land_size": await get_land_size(),
        "estate_type": await get_property_type(),
        "property_rooms": room_dict,
        # "property_features": {
        #     "hasPool": random.choice([True, False]),
        #     "hasGarage": random.choice([True, False]),
        #     "hasSolarPanels": random.choice([True, False]),
        #     "hasAirCon": random.choice([True, False]),
        #     "hasHeating": random.choice([True, False]),
        #     "hasNBN": random.choice([True, False])
        # }
    }


async def main(output_format="csv", output_filename="realestate_data"):
    geolocator = Nominatim(user_agent="geoapiExample")
    browser = await uc.start(headless=False)
    page = await browser.get()
    scraper = NoDriverScraper(browser, page)
    all_cards = []

    for page_num in range(1, 80):
        url = f"https://www.realestate.com.au/buy/in-nsw/list-{page_num}"
        response = await page.get(url)

        await scraper.wait_for_page()
        time.sleep(10)

        cards = await response.query_selector_all("article[data-testid='ResidentialCard']")
        if not cards:
            break

        for card in cards:
            try:
                card_details = await extract_card_details(card)
                raw_address = str(card_details.get("address"))
                cleaned_address = re.sub(r"^\s*\d+[/-]", "", raw_address.strip()) if raw_address else ""
                print(cleaned_address)

                location = geolocator.geocode(cleaned_address)
                if location:
                    card_details["lat"] = location.latitude
                    card_details["long"] = location.longitude
                all_cards.append(card_details)
            except Exception:
                pass

        time.sleep(2)
        break

    df = pd.json_normalize(all_cards)

    # Export
    path = f"{SAVE_LOCATION}/{output_filename}.{output_format}"
    if output_format == "csv":
        df.to_csv(path, index=False)
    elif output_format == "xlsx":
        df.to_excel(path, index=False)
    elif output_format == "json":
        df.to_json(path, orient="records", indent=4)
    else:
        raise ValueError(f"Unsupported export format: {output_format}")

    print(f"✅ Data saved to: {path}")


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

