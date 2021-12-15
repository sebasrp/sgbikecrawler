import traceback
import regex as re
import json
from decimal import Decimal

import requests
from tqdm import tqdm
import dateparser
from dateparser.search import search_dates

from vehicle_ad import VehicleAd


class CarousellAPI:
    BASE = "https://www.carousell.sg"
    SEARCH = "https://www.carousell.sg/api-service/search/cf/4.0/search/"
    DETAIL = "https://www.carousell.sg/api-service/listing/3.1/listings/"


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
            if len(coe_dates) > 0:
                coe_expiry_year = coe_dates[0][1].strftime("%Y/%m/%d")
        return coe_expiry_year, coe_expiry_details

    @staticmethod
    def retrieve_all_listings(bike_model, price_min="", price_max=""):
        print(f"retrieving listings from Carousell API")
        results = []
        search_params = {
            "bestMatchEnabled": True,
            "canChangeKeyword": True,
            "ccid": "1997",
            "count": 40,
            "countryCode": "SG",
            "countryId": "1880251",
            "filters":[
                {
                    "fieldName": "price",
                    "rangedFloat": {
                        "end":{"value": price_max},
                        "start":{"value": price_min}
                    }
                },
                {
                    "fieldName": "condition_v2",
                    "idsOrKeywords":{"value":["USED"]}
                },
            ],
            "includeSuggestions": True,
            "locale": "en",
            "prefill": {
                "prefill_condition_v2": "USED",
                "prefill_price_end": price_max,
                "prefill_price_start": price_min,
                "prefill_sort_by":"3"
            },
            "query": bike_model,
            "sortParam":{"fieldName": "3"}
        }
        response_data = []
        try:
            r = requests.post(CarousellAPI.SEARCH, data=search_params)
            response_data = r.json()['data']['results']
        except Exception:
            print(traceback.format_exc())

        #print(f"response_data: {json.dumps(response_data)}")

        for listing in tqdm(response_data):
            if "listingCard" in listing.keys():
                listing_data = listing["listingCard"]

                title = listing_data["title"]
                listing_id = listing_data['id']
                url = f"{CarousellAPI.BASE}/p/{listing_id}"

                try:
                    r_listing = requests.post(f"{CarousellAPI.DETAIL}/{listing_id}/detail")
                    listing_data = r_listing.json()['data']['screens'][0]['meta']['default_value']
                    listing_headers = r_listing.json()['data']['screens'][0]['groups']
                    print(f"listing_data: {json.dumps(listing_data)}")

                    price = listing_data['price']
                    if Decimal(price) < int(price_min) or Decimal(price) > int(price_max):
                        continue

                    posted_dt = dateparser.parse(
                        listing_data['time_created'],
                        settings={"PREFER_DAY_OF_MONTH": "first"},
                    )
                    posted_date = posted_dt.strftime("%Y/%m/%d")
                    bike_type = ""
                    description_text = listing_data['description']
                    coe_expiry_year, coe_expiry_details = CarousellAPI.retrieve_listing_coe(
                        description_text
                    )

                    bike_ad = VehicleAd(
                        source="Carousell",
                        title=title,
                        url=url,
                        coe_expiry_year=coe_expiry_year,
                        coe_expiry_details=coe_expiry_details,
                        price=price,
                        posted_date=posted_date,

                    )
                    results.append(bike_ad)
                except Exception:
                    print(traceback.format_exc())
        return results
