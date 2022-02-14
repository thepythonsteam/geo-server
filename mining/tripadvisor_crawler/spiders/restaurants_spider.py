import scrapy
import json
import re

from bs4 import BeautifulSoup


class RestaurantsSpider(scrapy.Spider):
    name = "restaurants"

    cities_filename = "cities.json"
    output_filename = "restaurants.json"

    hrefs_pattern = "/Restaurant_Review(?:[-\\w.]|(?:%[\\da-fA-F]{2}))+"
    home_url = "https://www.tripadvisor.ru/"

    def start_requests(self):
        with open(self.cities_filename, "r") as cities_file:
            datastore = json.load(cities_file)
            for city in datastore:
                yield scrapy.Request(
                    url=city["url"], callback=self.parse_restaurants_urls
                )

    def parse_restaurants_urls(self, response):
        html = response.body.decode("utf-8")
        restaurants_urls = re.findall(self.hrefs_pattern, html)

        for url in restaurants_urls:
            restaurant_url = self.home_url + url
            yield scrapy.Request(url=restaurant_url, callback=self.parse)

        next_page_href = response.css('.nav.next ::attr("href")').get() or None

        if next_page_href is not None:
            next_page = self.home_url + next_page_href
            yield response.follow(next_page, self.parse_restaurants_urls)

    def parse(self, response):
        html = response.body
        soup = BeautifulSoup(html, "html.parser")

        assessments_container = soup.find("div", class_="choices")
        assessments = (
            assessments_container.find_all("div", class_="ui_checkbox item")
            if assessments_container
            else []
        )
        assessments_data = {}

        for assessment in assessments:
            metric_name = assessment.find("input").get("value") + "_star"
            review_amount = assessment.find("span", class_="row_num").get_text()

            assessments_data[metric_name] = review_amount

        title = soup.find("h1", class_="fHibz")
        rating = soup.find("span", class_="fdsdx")
        phone_number = soup.find("span", class_="fhGHT")
        review_count = soup.find("a", class_="dUfZJ")
        street_address = soup.find("span", class_="brMTW")
        work_time = soup.find("span", class_="cSjwK")
        geodata = soup.find("div", class_="dsMUL f e")
        # price = soup.find("div", class_="cfvAV")
        full_data = soup.find("div", class_="guXtP")
        price = soup.find_all("div", class_="cfvAV")
        if len(price) > 0:
            price = price[0]
        else:
            price = None

        locality = soup.find_all("div", class_="cfvAV")
        if len(locality) > 1:
            locality = locality[1]
        elif len(locality) == 1:
            locality = locality[0]
        else:
            locality = None

        yield {
            "url": response.url,
            "title": title.get_text() if title else "",
            "rating": rating.get_text() if rating else "",
            "review_count": review_count.get_text() if review_count else "",
            "street_adress": street_address.get_text() if street_address else "",
            "work_time": work_time.get_text() if work_time else "",
            "geodata": geodata.get_text() if geodata else "",
            "full_data": full_data.get_text() if full_data else "",
            "price": price.get_text() if price else "",
            "locality": locality.get_text() if locality else "",
            "assessments_info": assessments_data,
            "phone_number": phone_number.get_text() if phone_number else "",
        }
