import scrapy
import re

home_url = "https://www.tripadvisor.ru"


class CitiesSpider(scrapy.Spider):
    name = "cities"
    start_urls = [
        home_url + "/Restaurants-g294459-Russia.html",
    ]

    # This method parses data from first cities page because of different structure
    def parse(self, response):
        for city in response.css(".geo_wrap"):
            try:
                name = re.search(
                    "Рестораны (.+)", city.css(".geo_name a::text").get()
                ).group(1)
            except AttributeError:
                name = city.css(".geo_name a::text").get()
            yield {
                "name": name,
                "url": home_url + city.css(".geo_name a::attr(href)").get(),
            }
        yield scrapy.Request(
            url=home_url + "/Restaurants-g294459-oa20-Russia.html",
            callback=self.parse_from_second_page,
        )

    # This method parses data from second to last cities pages
    def parse_from_second_page(self, response):
        for city in response.css(".geoList li"):
            try:
                name = re.search("Рестораны (.+)", city.css("a::text").get()).group(1)
            except AttributeError:
                name = city.css("a::text").get()
            yield {
                "name": name,
                "url": home_url + city.css("a::attr(href)").get(),
            }

        next_page = (
            home_url
            + response.css('.pgLinks a.guiArw.sprite-pageNext ::attr("href")').get()
        )

        if next_page is not None:
            yield response.follow(next_page, self.parse_from_second_page)
