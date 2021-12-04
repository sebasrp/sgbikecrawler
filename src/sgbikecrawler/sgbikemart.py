import regex as re
import urllib.parse

from bs4 import BeautifulSoup
import requests


class SGBikeMart:
    BASE = "https://www.sgbikemart.com.sg/"
    URL = "https://www.sgbikemart.com.sg/listing/usedbikes/listing/"

    @staticmethod
    def retrieve_page(url):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")
        return soup

    @staticmethod
    def retrieve_body_section(soup, section_str):
        section_value = None
        string_div = soup.find(text=re.compile(section_str))
        if string_div is not None:
            section_value = string_div.find_next(
                "div", {"class": ["text-start"]}
            ).text.strip()
        return section_value

    @staticmethod
    def retrieve_price(soup):
        price_value = ""
        price = soup.find("sup", text="SGD")
        if price is not None:
            parent = price.parent
            price_value_group = re.search(r"SGD\$\K\S+", parent.text)
            price_value = price_value_group.group(0).strip()
        return price_value

    @staticmethod
    def retrieve_total_pages(soup):
        total_pages = -1
        pattern = re.compile("last")
        last_page_qs = soup.find("a", text=pattern, attrs={"class": "page-link"})[
            "href"
        ]
        last_page_qs = (
            last_page_qs[1:] if last_page_qs.startswith("?") else last_page_qs
        )
        total_pages = dict(urllib.parse.parse_qsl(last_page_qs))
        total_pages = total_pages["page"]
        return int(total_pages)

    def retrieve_all_listings(self, bike_model):
        results = []

        page_url = f"{SGBikeMart.URL}?bike_model={bike_model}"
        init_page = SGBikeMart.retrieve_page(page_url)
        total_pages = SGBikeMart.retrieve_total_pages(init_page)

        for page_number in range(1, total_pages):
            page_url = f"{SGBikeMart.URL}?page={page_number}&bike_model={bike_model}"
            retrieved_page = SGBikeMart.retrieve_page(page_url)
            print(f"crawling page {page_number}, url: {page_url}")
            all_bikes = retrieved_page.select("div.row > div.col-lg-9 > div.card")

            for bike in all_bikes:
                ad_url = ""
                ad_title = ""
                header = bike.find("div", {"class": ["card-header"]})

                if header is None:
                    continue

                link = header.find("a", href=True)
                if link is not None:
                    ad_url = f"{SGBikeMart.BASE}{link['href']}"
                    ad_title = link.get_text().strip()
                body = bike.find(name="div", class_="card-body")
                if body is not None:
                    reg_date = SGBikeMart.retrieve_body_section(body, "Reg Date")
                    capacity = SGBikeMart.retrieve_body_section(body, "Capacity")
                    bike_type = SGBikeMart.retrieve_body_section(body, "Vehicle Type")
                    mileage = SGBikeMart.retrieve_body_section(body, "Mileage")
                    price = SGBikeMart.retrieve_price(body)

                    bike_ad = {
                        "title": ad_title,
                        "url": ad_url,
                        "reg_date": reg_date,
                        "capacity": capacity,
                        "bike_type": bike_type,
                        "mileage": mileage,
                        "price": price,
                    }
                    results.append(bike_ad)

        print(f"Number of items: {len(results)}")

        return results
