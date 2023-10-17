import scrapy

from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from scrapy_selenium.selenium_response import SeleniumResponse


class HotelsSpider(scrapy.Spider):
    name = "hotels"
    allowed_domains = ["www.booking.com", "secure.booking.com"]
    start_urls = [
        "https://www.booking.com/searchresults.en-gb.html"
        "?ss=San+Pedro+de+Atacama&ssne=San+Pedro+de+Atacama"
        "&ssne_untouched=San+Pedro+de+Atacama"
        "&highlighted_hotels=329344&lang=en-gb&checkin="
        f"{(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}&checkout"
        f"={(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')}"]

    def parse(
            self,
            response: SeleniumResponse,
            offset: int = 0,
            **kwargs
    ):
        elements_number = self._get_elements_number(response)
        print(self.start_urls[0])

        for link in self._get_all_hotels_links(response):
            yield self._get_lowest_price_room_info(
                link=link, response=response
            )

        if offset <= elements_number:
            offset += 25
            yield scrapy.Request(
                f"{self.start_urls[0]}&offset={offset}",
                callback=self.parse,
                cb_kwargs=dict(offset=offset)
            )

    @staticmethod
    def _get_all_hotels_links(response: SeleniumResponse) -> str:
        for hotel in response.css(
                "div[data-testid = 'property-card']"
        ):
            yield hotel.css(
                "a[data-testid = 'title-link']::attr(href)"
            ).extract()[0]

    @staticmethod
    def _get_elements_number(response: SeleniumResponse) -> int:
        sentence = response.css(
            'div[data-component="arp-header"] h1::text'
        ).get().split()
        for word in sentence:
            if word.isnumeric():
                return int(word)

    def _get_lowest_price_room_info(
            self, link: str, response: SeleniumResponse
    ):

        response.driver.get(link)
        row = self._get_lowest_prise_room(response)

        Select(row.find_element(
            By.CSS_SELECTOR, ".hprt-nos-select"
        )).select_by_index(1)
        reserve_button = response.driver.find_element(
            By.CSS_SELECTOR, ".hprt-reservation-cta button"
        )
        reserve_button.click()

        detail_button = response.driver.find_element(
            By.CSS_SELECTOR, "button[data-bui-ref = 'accordion-button']"
        )
        detail_button.click()
        room_name = " ".join(response.driver.find_element(
            By.CSS_SELECTOR,
            ".bui-text--variant-emphasized_2"
        ).text.split()[2:])

        price_currency = response.driver.find_element(
            By.CSS_SELECTOR, "span[data-component='core/animate-price']"
        )

        return {
            "Room name": room_name,
            "price": round(
                float(price_currency.get_attribute("data-value")), 2
            ),
            "Currency": price_currency.get_attribute("data-currency")
        }

    def _get_lowest_prise_room(self, response: SeleniumResponse):
        rows = response.driver.find_elements(
            By.CSS_SELECTOR, "#hprt-table .e2e-hprt-table-row"
        )
        response.driver.find_elements(By.CSS_SELECTOR, ".hprt-reservation-cta")
        min_price_row = rows[0]
        for row in rows[1:]:
            adults_sleeps = len(row.find_elements(
                By.CSS_SELECTOR, ".c-occupancy-icons__adults .bicon-occupancy"
            ))
            if (
                    adults_sleeps == 2
                    and self._get_room_price(row)
                    < self._get_room_price(min_price_row)
            ):
                min_price_row = row
        return min_price_row

    @staticmethod
    def _get_room_price(row):
        return int(row.find_element(
            By.CSS_SELECTOR,
            ".bui-price-display__value .prco-valign-middle-helper"
        ).text.split()[-1].replace(",", ""))


