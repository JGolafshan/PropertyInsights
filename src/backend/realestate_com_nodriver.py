#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 02/09/2025
Author: Joshua David Golafshan
"""

import asyncio
import re
import logging
import nodriver as uc
from geopy.geocoders import Nominatim
from nodriver.core.element import Element
from src.backend.database import insert_property, init_db
from src.backend.property_pydantic_model import *

NA_VALUE = "N/A"
geolocator = Nominatim(user_agent="geoapiExample")

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
    """
    Safely execute an async function and return default value on error.

    Args:
        fn: Async function to execute
        default: Default value to return on error

    Returns:
        Function result or default value
    """
    try:
        return await fn()
    except Exception as e:
        logging.getLogger(__name__).debug(f"safe_find_async error in {fn.__name__}: {e}")
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

def parse_price(price_text: str) -> Optional[PropertyPrice]:
    if not price_text:
        return None

    text = price_text.lower().strip()

    # Ignore non-numeric pricing
    ignore_terms = [
        "contact", "auction", "expression",
        "price on application", "poa"
    ]
    if any(term in text for term in ignore_terms):
        return None

    # Helper to convert "$1.2m" -> 1200000
    def to_number(value: str) -> float:
        value = value.replace(",", "").strip()
        multiplier = 1

        if value.endswith("m"):
            multiplier = 1_000_000
            value = value[:-1]
        elif value.endswith("k"):
            multiplier = 1_000
            value = value[:-1]

        return float(value) * multiplier

    # Extract numeric values
    numbers = re.findall(r"\$?\s*([\d,.]+[mk]?)", text)
    values = [to_number(n) for n in numbers]

    # Case: "$X - $Y"
    if "-" in text and len(values) >= 2:
        return PropertyPrice(
            actual_price=0.0,
            min_price_guide=values[0],
            max_price_guide=values[1],
        )

    # Case: "greater than $X", "from $X", "$X+"
    if any(term in text for term in ["greater", "from", "+", "over"]):
        return PropertyPrice(
            actual_price=0.0,
            min_price_guide=values[0],
            max_price_guide=0.0,
        )

    # Case: "$X"
    if len(values) == 1:
        return PropertyPrice(
            actual_price=values[0],
            min_price_guide=values[0],
            max_price_guide=values[0],
        )

    return None


async def extract_card_details(card):
    try:
        price_text = await safe_find_async(
            lambda: get_text_from("span.property-price", card)
        )
        address = await safe_find_async(
            lambda: get_text_from("h2.residential-card__address-heading", card)
        )
        image_url = await safe_find_async(
            lambda: get_attr_from("div.property-image", "data-url", card)
        )
        url_link = await safe_find_async(
            lambda: get_attr_from(
                "h2.residential-card__address-heading a", "href", card
            )
        )

        async def get_land_size():
            land_li = await card.query_selector("li[aria-label*='land size'] p")
            return land_li.text if land_li else None

        if not url_link:
            return None

        url_complete = "https://www.realestate.com.au" + url_link

        residential_data = await safe_find_async(
            lambda: card.query_selector("ul.residential-card__primary")
        )
        if not residential_data:
            return None


        room_items = await safe_find_async(
            lambda: residential_data.query_selector_all("li"), []
        )

        standard_room_types = {
            "bedroom": "bedrooms",
            "bathroom": "bathrooms",
            "car space": "car_spaces",
            "with study": "studies",
        }

        attributes: list[PropertyAttributes] = []

        for room in room_items:
            aria_label = room.attrs.get("aria-label", "")
            if not aria_label:
                continue

            aria_label = aria_label.lower()

            p = await room.query_selector("p")
            if not p or not p.text or not p.text.isdigit():
                continue

            count = int(p.text)

            for key, normalized_name in standard_room_types.items():
                if key in aria_label:
                    attributes.append(
                        PropertyAttributes(
                            attribute_name=normalized_name,
                            attribute_count=count,
                        )
                    )
                    break

        # -------------------------
        # Property type
        # -------------------------
        async def get_property_type():
            ps = await residential_data.query_selector_all("p")
            return ps[-1].text if ps else "UNKNOWN"

        property_type = await get_property_type()

        # -------------------------
        # Price (basic parsing)
        # -------------------------
        images = []
        if image_url:
            images.append(
                Images(
                    image_path=image_url,
                    is_primary=True,
                )
            )

        address_model = None

        if address:
            cleaned_address = re.sub(r"^\s*\d+[/-]", "", address.strip())

            try:
                loop = asyncio.get_running_loop()
                # Add timeout to prevent hanging on slow geocoding
                location = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, lambda: geolocator.geocode(cleaned_address)
                    ),
                    timeout=5.0
                )
            except (Exception, asyncio.TimeoutError) as e:
                logging.getLogger(__name__).debug(f"Geocoding failed for {cleaned_address}: {e}")
                location = None

            if location:
                address_model = PropertyAddress(
                    address_raw=cleaned_address,
                    latitude=location.latitude,
                    longitude=location.longitude,
                )

        property_data = Property(
            url=url_complete,
            sale_type="Active",
            land_size=await get_land_size(),
            property_type=property_type,
            price=parse_price(price_text),
            images=images,
            address=address_model,
            features=[],
            attributes=attributes,
        )

        logging.getLogger(__name__).info(f"Extracted property: {property_data.address.address_raw if property_data.address else 'Unknown'}")
        return property_data

    except Exception as e:
        print("an error occured")
        return None



async def main(output_format="csv", output_filename="realestate_data"):
    browser = await uc.start(headless=False)
    page = await browser.get()
    scraper = NoDriverScraper(browser, page)
    await init_db()

    state_list = ["nsw", "wa", "act", "sa", "nt", "qld", "tas"]
    for state in state_list:
        for page_num in range(1, 40):
            url = f"https://www.realestate.com.au/buy/in-{state}/list-{page_num}"
            response = await page.get(url)

            await scraper.wait_for_page()
            # Reduced sleep time - page is ready after wait_for_page()
            await asyncio.sleep(2)

            cards = await response.query_selector_all(
                "article[data-testid='ResidentialCard']"
            )
            if not cards:
                break

            for card in cards:
                try:
                    property_data = await extract_card_details(card)
                    if not property_data:
                        continue

                    await insert_property(property_data)

                except Exception as e:
                    logging.getLogger(__name__).error(f"Error processing card on page {page_num}: {e}", exc_info=True)



if __name__ == "__main__":
    uc.loop().run_until_complete(main())

