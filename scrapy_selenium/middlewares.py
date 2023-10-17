from selenium import webdriver

from hotel_scrapper.middlewares import HotelScrapperDownloaderMiddleware
from scrapy_selenium.selenium_response import SeleniumResponse


class SeleniumMiddleware(HotelScrapperDownloaderMiddleware):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1920, 1080, self.driver.window_handles[0])

    def process_request(self, request, spider):
        self.driver.get(request.url)

        body = self.driver.page_source
        return SeleniumResponse(
            url=self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request,
            driver=self.driver
        )

    def spider_closed(self):
        self.driver.quit()
