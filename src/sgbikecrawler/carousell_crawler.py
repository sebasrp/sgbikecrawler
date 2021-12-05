import regex as re
import urllib.parse

from bs4 import BeautifulSoup
import requests

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
    def retrieve_all_listings(bike_model):
        results = []
        page_url = f"{Carousell.SEARCH}{urllib.parse.quote(bike_model)}?{urllib.parse.urlencode({'condition_v2':'USED'})}"
        search_results = Carousell.retrieve_page(page_url)

        for card in search_results.find_all("div", {"class": "D_BM"}):
            info = card.find("a", {"class": "D_ic", "href": re.compile("^\/p\/")})
            preview = info.find("img")
            title = info.find("img", {"src": re.compile("\S*_thumbnail\S*")}).get(
                "title"
            )  # title text of img has same text as ad title
            price_string = Carousell.retrieve_price(info)
            href = info.get("href")
            url = Carousell.BASE + href

            bike_ad = VehicleAd(
                source="Carousell", title=title, url=url, price=price_string
            )
            results.append(bike_ad)

        return results
