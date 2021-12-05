import regex as re
import urllib.parse

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
                price = price_group.group(0).strip()
        return price

    @staticmethod
    def retrieve_listing_coe(soup):
        coe_expiry_year = ""
        coe_expiry_details = ""
        description_div = soup.find("div", {"class": "D_PA"})
        description_text = description_div.find("p").text
        COE_expiry_search = re.search(r"(?i:COE.+)(20[0-9]*)", description_text)
        if COE_expiry_search is not None:
            coe_expiry_year = COE_expiry_search.group(1).strip()
            coe_expiry_details = COE_expiry_search.group(0).strip()
        return coe_expiry_year, coe_expiry_details

    @staticmethod
    def retrieve_all_listings(bike_model):
        results = []
        page_url = f"{Carousell.SEARCH}{urllib.parse.quote(bike_model)}?{urllib.parse.urlencode({'condition_v2':'USED'})}"
        search_results = Carousell.retrieve_page(page_url)

        for card in tqdm(search_results.find_all("div", {"class": "D_BM"})):
            info = card.find("a", {"class": "D_ic", "href": re.compile("^\/p\/")})
            title = info.find("img", {"src": re.compile("\S*_thumbnail\S*")}).get(
                "title"
            )  # title text of img has same text as ad title
            price_string = Carousell.retrieve_price(info)
            href = info.get("href")
            url = Carousell.BASE + href

            # we now need to retrieve the remaining data from the listing page
            listing_page = Carousell.retrieve_page(url)
            coe_expiry_year, coe_expiry_details = Carousell.retrieve_listing_coe(
                listing_page
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
