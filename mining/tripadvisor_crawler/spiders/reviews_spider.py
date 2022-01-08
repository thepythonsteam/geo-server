import scrapy
import json
import re

from bs4 import BeautifulSoup


class ReviewsSpider(scrapy.Spider):
    name = "reviews"

    restaurants_filename = "restaurants.json"
    output_filename = "reviews.json"
    home_url = "https://www.tripadvisor.ru/"

    def start_requests(self):
        with open(self.restaurants_filename, "r") as restaurants_file:
            datastore = json.load(restaurants_file)

            for restaurant in datastore:
                yield scrapy.Request(url=restaurant["url"], callback=self.parse)

    def parse(self, response):
        html = response.body
        soup = BeautifulSoup(html, "html.parser")

        reviews = soup.find_all("div", class_="reviewSelector")
        reviews_data = {}

        for review in reviews:
            user_info = review.find("div", class_="info_text pointer_cursor") or ""
            # user_location_info = user_info.find("div", class_="userLoc") or ""
            # user_location = (
            #     user_location_info.find("strong").get_text()
            #     if user_location_info
            #     else ""
            # )

            restaurant_name = soup.find("h1", class_="fHibz")
            url = review.find("a", class_="title")
            date = review.find("span", class_="ratingDate")
            review_title = review.find("span", class_="noQuotes")
            review_body = review.find("p", class_="partial_entry")
            date_of_visit = review.find("div", class_="prw_reviews_stay_date_hsx")

            reviews_data.update(
                {
                    "restaurant_name": restaurant_name.get_text() if restaurant_name else "",
                    "url": self.home_url + url["href"] or "",
                    "username": user_info.get_text() if user_info and user_info.get_text() else "",
                    "date": date.get_text() if date else "",
                    "review_title": review_title.get_text() if review_title else "",
                    "review_body": "",
                    "date_of_visit": date_of_visit.get_text() if date_of_visit else "",
                }
            )

            for x in range(1, 6):
                if review.find("span", class_=f"ui_bubble_rating bubble_{x}0"):
                    reviews_data.update({"stars_amount": x})

            # user_badging_block = review.find("div", class_="memberOverlay simple container moRedesign")
            # badgings = review.findAll("span", class_="badgeTextReviewEnhancements")
            #
            # if user_badging_block.find("span", class_="badgeTextReviewEnhancements"):
            #     reviews_data.update({"reviews_by_user_amount": badgings[0].get_text()})
            #
            # if user_badging_block.find("span", class_="badgeTextReviewEnhancements"):
            #     reviews_data.update({"review_likes_amount": badgings[2].get_text()})
            # else:
            #     reviews_data.update({"review_likes_amount": ""})


            if review_body and "...Еще" in review_body.get_text():
                yield scrapy.Request(
                    url=self.home_url + url["href"],
                    callback=self.parse_full,
                    meta=reviews_data,
                )
            else:
                reviews_data.update(
                    {"review_body": review_body.get_text() if review_body else ""}
                )
                yield reviews_data

        next_page_href = response.css('.nav.next ::attr("href")').get() or None

        if next_page_href is not None:
            next_page = self.home_url + next_page_href
            yield response.follow(next_page, self.parse)

    def parse_full(self, response):
        html = response.body
        soup = BeautifulSoup(html, "html.parser")
        key_list = [
            "restaurant_name",
            "url",
            "username",
            "date",
            "review_title",
            "review_body",
            "date_of_visit",
            "stars_amount",
        ]
        meta_copy = response.meta.copy()
        result = {key: meta_copy[key] for key in key_list}
        result.update(
            {"review_body": soup.find("p", class_="partial_entry").get_text()}
        )
        yield result
