class VehicleAd(object):
    def __init__(
        self,
        source,
        title,
        url,
        price,
        posted_date="",
        coe_expiry_year="",
        coe_expiry_details="",
        capacity="",
        vehicle_type="",
        mileage="",
        paid_ad="",
        dealer_ad="",
        direct_seller_ad="",
    ) -> None:
        super().__init__()
        self.source = source
        self.title = title
        self.url = url
        self.coe_expiry_year = coe_expiry_year
        self.coe_expiry_details = coe_expiry_details
        self.price = price
        self.posted_date = posted_date
        self.capacity = capacity
        self.vehicle_type = vehicle_type
        self.mileage = mileage
        self.paid_ad = paid_ad
        self.dealer_ad = dealer_ad
        self.direct_seller_ad = direct_seller_ad

    def to_dict(self):
        return {
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "coe_expiry_year": self.coe_expiry_year,
            "coe_expiry_details": self.coe_expiry_details,
            "price": self.price,
            "posted_date": self.posted_date,
            "capacity": self.capacity,
            "vehicle_type": self.vehicle_type,
            "mileage": self.mileage,
            "paid_ad": self.paid_ad,
            "dealer_ad": self.dealer_ad,
            "direct_seller_ad": self.direct_seller_ad,
        }
