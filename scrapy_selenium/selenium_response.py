from typing import Any

from scrapy.http import HtmlResponse
from selenium.webdriver import Chrome


class SeleniumResponse(HtmlResponse):
    def __init__(self, driver: Chrome, *args: Any, **kwargs: Any):
        self.driver = driver
        super().__init__(*args, **kwargs)
