from sgbikemart_crawler import SGBikeMart
from carousell_crawler import Carousell


class SGBikeCrawler:
    @staticmethod
    def retrieve_all_listings(bike_model):
        bike_ads = []
        bike_ads += SGBikeMart.retrieve_all_listings(bike_model=bike_model)
        bike_ads += Carousell.retrieve_all_listings(bike_model=bike_model)

        results = []
        for bike in bike_ads:
            results.append(bike.to_dict())
        return results
