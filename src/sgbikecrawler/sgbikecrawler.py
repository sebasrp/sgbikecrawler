from sgbikemart_crawler import SGBikeMart


class SGBikeCrawler:
    @staticmethod
    def retrieve_all_listings(bike_model):
        sgbikemart_bikes = SGBikeMart.retrieve_all_listings(bike_model=bike_model)

        results = []
        for bike in sgbikemart_bikes:
            results.append(bike.to_dict())
        return results
