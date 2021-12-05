import regex as re
import datetime
import urllib.parse

from bs4 import BeautifulSoup
import requests

from vehicle_ad import VehicleAd


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
    def has_button_text(soup, text):
        buttons_list = soup.find_all("button")
        for button in buttons_list:
            if text in button.text:
                return True
        return False

    @staticmethod
    def retrieve_posted_date(soup):
        date = ""
        small_list = soup.find_all("small")
        for item in small_list:
            date_group = re.search(r"Posted on :\n\K\S+", item.text)
            if date_group is not None:
                date = date_group.group(0).strip()
        return date

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

    @staticmethod
    def retrieve_all_listings(bike_model):
        results = []

        page_url = (
            f"{SGBikeMart.URL}?{urllib.parse.urlencode({'bike_model':bike_model})}"
        )
        init_page = SGBikeMart.retrieve_page(page_url)
        total_pages = SGBikeMart.retrieve_total_pages(init_page)
        print(f"Search result has {total_pages} pages... let's get started!")

        for page_number in range(1, total_pages + 1):
            url_vars = {"page": page_number, "bike_model": bike_model}
            page_url = f"{SGBikeMart.URL}?{urllib.parse.urlencode(url_vars)}"
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
                    reg_date_datetime = datetime.datetime.strptime(reg_date, "%d/%m/%Y")
                    coe_datetime = reg_date_datetime.replace(
                        year=reg_date_datetime.year + 10
                    )
                    coe_expiry_year = coe_datetime.year
                    coe_expiry_details = coe_datetime.strftime("%Y/%m/%d")
                    capacity = SGBikeMart.retrieve_body_section(body, "Capacity")
                    bike_type = SGBikeMart.retrieve_body_section(body, "Vehicle Type")
                    mileage = SGBikeMart.retrieve_body_section(body, "Mileage")
                    price = SGBikeMart.retrieve_price(body)

                    date_posted = SGBikeMart.retrieve_posted_date(body)
                    is_paid = SGBikeMart.has_button_text(body, "Paid Ad")
                    is_dealer = SGBikeMart.has_button_text(body, "Dealer Ad")
                    is_direct_seller = SGBikeMart.has_button_text(body, "Direct Seller")

                    bike_ad = VehicleAd(
                        source="SGBikeMart",
                        title=ad_title,
                        url=ad_url,
                        posted_date=date_posted,
                        price=price,
                        coe_expiry_year=coe_expiry_year,
                        coe_expiry_details=coe_expiry_details,
                        capacity=capacity,
                        vehicle_type=bike_type,
                        mileage=mileage,
                        paid_ad=is_paid,
                        dealer_ad=is_dealer,
                        direct_seller_ad=is_direct_seller,
                    )
                    results.append(bike_ad)

        print(f"Number of items: {len(results)}")

        return results
