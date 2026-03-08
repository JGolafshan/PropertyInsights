#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 02/09/2025
Author: Joshua David Golafshan
"""

import re
import logging
import nodriver as uc
from geopy.geocoders import Nominatim
from selectolax.parser import HTMLParser
from src.backend.property_pydantic_model import *
from src.backend.database import insert_property, init_db

NA_VALUE = "N/A"
logging.basicConfig(level=logging.INFO)
geolocator = Nominatim(user_agent="geoapiExample")
SELECTORS = {
    "property_card": "article[data-testid='ResidentialCard']",
    "price": "span.property-price",
    "address": "h2.residential-card__address-heading",
    "image": "div.property-image",
    "url": "h2.residential-card__address-heading a",
    "landsize": "li[aria-label*='land size'] p",
    "residential_data": "ul.residential-card__primary"
}


class NoDriverScraper:
    def __init__(self, browser: uc.Browser, page: uc.Tab):
        self.browser = browser
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    async def wait_for_page(self):
        await self.page.evaluate(
            """
            new Promise((resolve) => {
                function waitForIdleAfterLoad() {

                    if ('requestIdleCallback' in window) {
                        requestIdleCallback(() => {
                            setTimeout(resolve, 300);
                        }, {timeout: 3000});

                    } else {
                        setTimeout(resolve, 500);
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

def parse_price(price_text: str) -> Optional[PropertyPrice]:

    if not price_text:
        return None

    text = price_text.lower().strip()

    ignore_terms = [
        "contact",
        "auction",
        "expression",
        "price on application",
        "poa"
    ]

    if any(term in text for term in ignore_terms):
        return None

    def to_number(value: str):

        value = value.replace(",", "").strip()

        multiplier = 1

        if value.endswith("m"):
            multiplier = 1_000_000
            value = value[:-1]

        elif value.endswith("k"):
            multiplier = 1_000
            value = value[:-1]

        return float(value) * multiplier

    numbers = re.findall(r"\$?\s*([\d,.]+[mk]?)", text)

    values = [to_number(n) for n in numbers]

    if "-" in text and len(values) >= 2:
        return PropertyPrice(
            actual_price=0.0,
            min_price_guide=values[0],
            max_price_guide=values[1],
        )

    if any(term in text for term in ["greater", "from", "+", "over"]):
        return PropertyPrice(
            actual_price=0.0,
            min_price_guide=values[0],
            max_price_guide=0.0,
        )

    if len(values) == 1:
        return PropertyPrice(
            actual_price=values[0],
            min_price_guide=values[0],
            max_price_guide=values[0],
        )

    return None

def extract_card_details(card):

    try:

        price_el = card.css_first(SELECTORS["price"])
        address_el = card.css_first(SELECTORS["address"])
        image_el = card.css_first(SELECTORS["image"])
        url_el = card.css_first(SELECTORS["url"])
        land_el = card.css_first(SELECTORS["landsize"])

        price_text = price_el.text(strip=True) if price_el else NA_VALUE
        address = address_el.text(strip=True) if address_el else NA_VALUE

        image_url = image_el.attributes.get("data-url") if image_el else None
        url_link = url_el.attributes.get("href") if url_el else None
        land_size = land_el.text(strip=True) if land_el else None

        if not url_link:
            return None

        url_complete = "https://www.realestate.com.au" + url_link

        residential_data = card.css_first(SELECTORS["residential_data"])

        attributes: list[PropertyAttributes] = []

        if residential_data:

            room_items = residential_data.css("li")

            standard_room_types = {
                "bedroom": "bedrooms",
                "bathroom": "bathrooms",
                "car space": "car_spaces",
                "with study": "studies",
            }

            for room in room_items:

                aria_label = room.attributes.get("aria-label", "").lower()

                p = room.css_first("p")

                if not p:
                    continue

                count_text = p.text().strip()

                if not count_text.isdigit():
                    continue

                count = int(count_text)

                for key, normalized in standard_room_types.items():

                    if key in aria_label:

                        attributes.append(
                            PropertyAttributes(
                                attribute_name=normalized,
                                attribute_count=count
                            )
                        )

                        break

        property_type = "UNKNOWN"

        if residential_data:

            ps = residential_data.css("p")

            if ps:
                property_type = ps[-1].text().strip()

        images = []

        if image_url:

            images.append(
                Images(
                    image_path=image_url,
                    is_primary=True
                )
            )

        address_model = None

        if address:

            cleaned_address = re.sub(r"^\s*\d+[/-]", "", address.strip())

            try:

                location = geolocator.geocode(cleaned_address, timeout=5)

                if location:

                    address_model = PropertyAddress(
                        address_raw=cleaned_address,
                        latitude=location.latitude,
                        longitude=location.longitude
                    )

            except Exception:
                pass

        property_data = Property(
            url=url_complete,
            sale_type="Active",
            land_size=land_size,
            property_type=property_type,
            price=parse_price(price_text),
            images=images,
            address=address_model,
            features=[],
            attributes=attributes,
        )

        return property_data

    except Exception as e:

        logging.getLogger(__name__).error(f"Card parse failed: {e}")

        return None


async def main():
    browser = await uc.start(headless=False)
    page = await browser.get()
    scraper = NoDriverScraper(browser, page)

    await init_db()

    state_list = ["nsw", "wa", "act", "sa", "nt", "qld", "tas"]

    for state in state_list:

        for page_num in range(1, 40):

            url = f"https://www.realestate.com.au/buy/in-{state}/list-{page_num}"

            logging.info(f"Scraping {url}")

            await page.get(url)
            await scraper.wait_for_page()

            html = await page.get_content()
            parser = HTMLParser(html)

            cards = parser.css(SELECTORS["property_card"])

            if not cards:
                break

            for card in cards:

                property_data = extract_card_details(card)

                if not property_data:
                    continue

                logging.info(f"Extracted property data: {property_data}")

                try:
                    await insert_property(property_data)
                    pass

                except Exception as e:
                    logging.error(f"DB insert failed: {e}")


if __name__ == "__main__":
    uc.loop().run_until_complete(main())