import regex as re
import urllib.parse
from decimal import Decimal

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

from vehicle_ad import VehicleAd


class Carousell:
    BASE = "https://sg.carousell.com"
    SEARCH = "https://sg.carousell.com/search/"

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
                price = Decimal(re.sub(r"[^\d\-.]", "", price_group.group(0).strip()))
        return price

    @staticmethod
    def retrieve_description_fields(soup):
        bumped = bike_type = text = ""
        # we first locate the description header
        description_div_children = soup.find(
            "p", text=re.compile("Description")
        ).parent.findAll("div", recursive=False)

        header_div = description_div_children[0]
        text = description_div_children[1].text
        return bumped, bike_type, text

    @staticmethod
    def retrieve_listing_coe(listing_text):
        coe_expiry_year = ""
        coe_expiry_details = ""
        COE_expiry_search = re.search(r"(?i:COE.+)(20[0-9]*)", listing_text)
        if COE_expiry_search is not None:
            coe_expiry_year = COE_expiry_search.group(1).strip()
            coe_expiry_details = COE_expiry_search.group(0).strip()
        return coe_expiry_year, coe_expiry_details

    @staticmethod
    def retrieve_all_listings(bike_model):
        print(f"retrieving listings from Carousell")
        results = []
        page_url = f"{Carousell.SEARCH}{urllib.parse.quote(bike_model)}?{urllib.parse.urlencode({'condition_v2':'USED'})}"
        print(f"crawling page: {page_url}")
        search_results = Carousell.retrieve_page(page_url)
        bike_listings = search_results.find_all(
            "div", {"data-testid": re.compile("listing-card-[0-9]+")}
        )
        print(f"found {len(bike_listings)} listings...")

        for card in tqdm(bike_listings):
            info = card.find("a", {"href": re.compile("^\/p\/")})
            title = info.find("img", {"src": re.compile("\S*_thumbnail\S*")}).get(
                "title"
            )  # title text of img has same text as ad title
            price_string = Carousell.retrieve_price(info)
            href = info.get("href")
            url = Carousell.BASE + href

            # we now need to retrieve the remaining data from the listing page
            listing_page = Carousell.retrieve_page(url)
            bumped, bike_type, listing_text = Carousell.retrieve_description_fields(
                listing_page
            )
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
            )
            results.append(bike_ad)

        return results
