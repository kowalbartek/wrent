from time import sleep
import requests
from bs4 import BeautifulSoup
import xlsxwriter
import re
import functions_module as fm
from rental import Rental


# Rental Scraper - scrapes data from online sources, runs calculations and compiles them into a workbook
class RentalScraper:
    def __init__(self):
        self.session = requests.Session()
        self.workbook = None
        self.worksheet = None
        self.number_of_rentals = 0
        self.all_prices = []

    def create_workbook(self):
        # Function to create workbook with current time and date
        workbook = fm.workbook_name()
        self.workbook = xlsxwriter.Workbook(workbook)
        self.worksheet = self.workbook.add_worksheet()

    def write_to_excel(self, rental):

        # Function which writes our data to the workbook
        if not self.workbook:
            self.create_workbook()

        if self.number_of_rentals == 0:
            print("There are no rentals in your location.")
            return

        headers = ['Price', 'Address', 'Link', 'Bed Baths', 'Date Published', 'Description', 'County']

        # Write headers
        for col, header in enumerate(headers):
            self.worksheet.write(0, col, header)

        row = self.number_of_rentals

        # Write rental data
        self.worksheet.write(row, 0, rental.price)
        self.worksheet.write(row, 1, rental.address)
        self.worksheet.write(row, 2, rental.link)
        self.worksheet.write(row, 3, rental.bed_baths)
        self.worksheet.write(row, 4, rental.date_published)
        self.worksheet.write(row, 5, rental.description)
        self.worksheet.write(row, 6, rental.county)

    def scrape_rent(self, workbook_name_static=fm.workbook_name()):
        # Function for scraping data
        counties = [
            "antrim", "armagh", "carlow", "cavan", "clare", "cork", "derry", "donegal", "down", "dublin",
            "fermanagh", "galway", "kerry", "kildare", "kilkenny", "laois", "leitrim", "limerick", "longford",
            "louth", "mayo", "meath", "monaghan", "offaly", "roscommon", "sligo", "tipperary", "tyrone",
            "waterford", "westmeath", "wexford", "wicklow"
        ]

        # Run scraper for every county specified in list
        for county in counties:
            page_number = 1

            while True:
                base_url = f"https://www.rent.ie/houses-to-let/renting_{county}/page_{page_number}"
                res = self.session.get(base_url)
                soup = BeautifulSoup(res.text, "html.parser")

                # Find all search results & max pages for each search
                search_results = soup.find_all("div", class_="search_result")
                pages = soup.find_all("span", class_="page")

                # If page is empty
                if not pages:
                    last_page = 1
                else:
                    # Else, get last page number
                    last_page = int(pages[-1].contents[0])

                if not search_results:
                    break  # No more listings for this county

                # Loggers
                if page_number > last_page:
                    print(f"Scraping: {county.capitalize()}, 100%")
                else:
                    print(f"Scraping: {county.capitalize()}, page {page_number}/{last_page}")

                # Looping through results
                for search in search_results:
                    # *** PRICE SCRAPE SYNTAX ***
                    home_price = int(re.sub(r'\D+', '', search.h4.text))

                    # Further filtering
                    if "weekly" in str(search.h4.contents):
                        home_price *= 4

                    # *** ADDRESS SCRAPE SYNTAX ***
                    address_element = str(search.div.contents[3]
                                          .next_element.next_element
                                          .text).strip().split()
                    address = ' '.join(str(e) for e in address_element) if address_element else "N/A"

                    # *** HREF LINK SCRAPE SYNTAX ***
                    href = search.find("a")["href"]

                    # *** BED/BATH SCRAPE SYNTAX ***
                    bed_baths = search.h3.text.strip()

                    # *** PUBLISHED DATE SCRAPE SYNTAX ***
                    published_date = search.br.previous_element.previous_element.strip()[8:]
                    if "hours" in published_date:
                        published_date = str(round(int(published_date.split()[0]) / 24, 2)) + " days ago"
                    elif "months" in published_date:
                        published_date = str(round(int(published_date.split()[0]) * 28)) + " days ago"
                    elif "years" in published_date:
                        published_date = str(round(int(published_date.split()[0]) * 365)) + " days ago"

                    # *** DESCRIPTION SCRAPE SYNTAX ***
                    description = search.br.next_element[21:]

                    # Filling the information into Rental format
                    rental = Rental(home_price, address, href, bed_baths, published_date, description, county.upper())

                    # At this point, rental is valid therefore can increase number of rentals
                    self.number_of_rentals += 1

                    # Add price to total price
                    self.all_prices.append(home_price)

                    # Write rental to workbook
                    self.write_to_excel(rental)

                    # Sleep loop, for ethical scraping
                    sleep(.1)

                # Move to the next page
                page_number += 1

        # Calculation loggers & error handling
        if self.number_of_rentals > 0:
            print(f"Number of rentals: {self.number_of_rentals}")
            print(f'Average house price: €{round(sum(self.all_prices) / self.number_of_rentals)}')
        else:
            print("No rentals found.")

        # Close workbook
        if self.workbook:
            self.workbook.close()
            fm.save_to_json(workbook_name_static)


# Runner
if __name__ == "__main__":
    scraper = RentalScraper()
    scraper.scrape_rent()
