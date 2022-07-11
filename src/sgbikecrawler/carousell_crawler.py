import regex as re
import urllib.parse
from decimal import Decimal

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import warnings
import dateparser
from dateparser.search import search_dates

from vehicle_ad import VehicleAd

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class Carousell:
    BASE = "https://sg.carousell.com"
    SEARCH = (
        "https://www.carousell.sg/categories/motorcycles-108/motorcycles-for-sale-1592/"
    )

    @staticmethod
    def retrieve_page(url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        return soup

    @staticmethod
    def retrieve_price(soup):
        price = ""
        p_list = soup.find_all("p")
        for item in p_list:
            price_group = re.search(r"S\$[0-9,]*", item.text)
            if price_group is not None:
                price = str(
                    Decimal(re.sub(r"[^\d\-.]", "", price_group.group(0).strip()))
                )
        return price

    @staticmethod
    def retrieve_description_fields(soup):
        posted = bike_type = title = text = ""
        is_paid = False

        # we get the title:
        title = soup.find(
            "p", {"data-testid": "new-listing-details-page-desktop-text-title"}
        ).getText()

        # we first locate the description header
        description_div_children = soup.find(
            "p", text=re.compile("Description")
        ).parent.findAll("div", recursive=False)

        header_div = description_div_children[0]
        bumped_div = header_div.find("p", text=re.compile("Bumped"))
        if bumped_div is not None:
            posted_dt = dateparser.parse(
                bumped_div.find_next_sibling("p").text,
                settings={"PREFER_DAY_OF_MONTH": "first"},
            )
            posted = posted_dt.strftime("%Y/%m/%d")
            is_paid = True
        else:
            posted_div = header_div.find("p", text=re.compile("Posted"))
            if posted_div is not None:
                posted_dt = dateparser.parse(
                    posted_div.find_next_sibling("p").text,
                    settings={"PREFER_DAY_OF_MONTH": "first"},
                )
                posted = posted_dt.strftime("%Y/%m/%d")
        bike_type_div = header_div.find("p", text=re.compile("Type"))
        if bike_type_div is not None:
            bike_type = bike_type_div.find_next_sibling("p").text
        text = description_div_children[1].text
        return posted, bike_type, title, text, is_paid

    @staticmethod
    def retrieve_listing_coe(listing_text):
        coe_expiry_year = ""
        coe_expiry_details = ""
        COE_expiry_search = re.search(r"(?i:COE.+)(20[0-9]*)", listing_text)
        if COE_expiry_search is not None:
            coe_expiry_year = COE_expiry_search.group(1).strip()
            coe_expiry_details = COE_expiry_search.group(0).strip()

            coe_dates = search_dates(
                coe_expiry_details, settings={"PREFER_DAY_OF_MONTH": "first"}
            )
            if coe_dates is not None and len(coe_dates) > 0:
                coe_expiry_year = coe_dates[0][1].strftime("%Y/%m/%d")
        return coe_expiry_year, coe_expiry_details

    @staticmethod
    def retrieve_all_listings(bike_model, price_min="", price_max=""):
        print(f"retrieving listings from Carousell")
        results = []
        search_params = {
            "search": bike_model,
            "condition_v2": "USED",
            "price_start": price_min,
            "price_end": price_max,
            "sort_by": 3,  # most recent first (until we figure out how to load all results)
        }
        page_url = f"{Carousell.SEARCH}?{urllib.parse.urlencode(search_params)}"

        print(f"crawling page: {page_url}")
        search_results = Carousell.retrieve_page(page_url)
        bike_listings = search_results.find_all(
            "div", {"data-testid": re.compile("listing-card-[0-9]+")}
        )
        print(f"found {len(bike_listings)} listings...")

        for card in tqdm(bike_listings):
            info = card.find("a", {"href": re.compile("^\/p\/")})
            price_string = Carousell.retrieve_price(info)
            href = info.get("href")
            url = Carousell.BASE + href

            # we now need to retrieve the remaining data from the listing page
            listing_page = Carousell.retrieve_page(url)
            (
                posted,
                bike_type,
                title,
                listing_text,
                is_paid,
            ) = Carousell.retrieve_description_fields(listing_page)
            coe_expiry_year, coe_expiry_details = Carousell.retrieve_listing_coe(
                listing_text
            )

            bike_ad = VehicleAd(
                source="Carousell",
                title=title,
                url=url,
                price=price_string,
                coe_expiry_year=coe_expiry_year,
                coe_expiry_details=coe_expiry_details,
                posted_date=posted,
                vehicle_type=bike_type,
                paid_ad=is_paid,
            )
            results.append(bike_ad)

        return results
