# Rental Property Class - contains all properties we look for
class Rental:
    def __init__(self, price, address, link, bed_baths, date_published, description, county):
        self.price = price
        self.address = address
        self.link = link
        self.bed_baths = bed_baths
        self.date_published = date_published
        self.description = description
        self.county = county
