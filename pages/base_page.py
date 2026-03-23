import os
import time
from datetime import datetime
from typing import List

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.logger import get_logger


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

    def _take_screenshot(self, prefix: str = "failure") -> str:
        screenshots_dir = os.environ.get("SCREENSHOTS_DIR", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = os.path.join(screenshots_dir, f"{prefix}_{timestamp}.png")

        self.page.screenshot(path=path, full_page=True)
        self.logger.info(f"Screenshot saved: {path}")
        return path

    def select_dropdown_by_text(self, locators: List[str], text: str, timeout: int = 5000, retries: int = 2,
                                backoff: float = 0.5):
        last_error = None

        for attempt in range(1, retries + 1):
            self.logger.info(f"Select attempt {attempt}/{retries} for text='{text}'")

            for index, locator in enumerate(locators, start=1):
                try:
                    self.logger.info(f"Trying select locator #{index}: {locator}")
                    element = self.page.locator(locator).first
                    element.wait_for(state="visible", timeout=timeout)
                    element.select_option(label=text, timeout=timeout)
                    self.logger.info(f"Select succeeded with locator #{index}: {locator}")
                    return
                except PlaywrightTimeoutError as e:
                    last_error = e
                    self.logger.warning(f"Timeout on locator #{index}: {locator}")
                except Exception as e:
                    last_error = e
                    self.logger.warning(f"Select failed on locator #{index}: {locator} | error={e}")

            if attempt < retries:
                sleep_time = backoff * attempt
                self.logger.info(f"Retrying select after {sleep_time} seconds")
                time.sleep(sleep_time)

        self._take_screenshot("select_failure")
        raise RuntimeError(f"Could not select option '{text}'. locators={locators}, last_error={last_error}")
    def smart_click(self, locators: List[str], timeout: int = 5000, retries: int = 2, backoff: float = 0.5):
        last_error = None

        for attempt in range(1, retries + 1):
            self.logger.info(f"Click attempt {attempt}/{retries}")

            for index, locator in enumerate(locators, start=1):
                try:
                    self.logger.info(f"Trying click locator #{index}: {locator}")
                    element = self.page.locator(locator).first
                    element.wait_for(state="visible", timeout=timeout)
                    element.click(timeout=timeout)
                    self.logger.info(f"Click succeeded with locator #{index}: {locator}")
                    return
                except PlaywrightTimeoutError as e:
                    last_error = e
                    self.logger.warning(f"Timeout on locator #{index}: {locator}")
                except Exception as e:
                    last_error = e
                    self.logger.warning(f"Click failed on locator #{index}: {locator} | error={e}")

            if attempt < retries:
                sleep_time = backoff * attempt
                self.logger.info(f"Retrying click after {sleep_time} seconds")
                time.sleep(sleep_time)

        self._take_screenshot("click_failure")
        raise Exception(f"Could not click any locator. locators={locators}, last_error={last_error}")

    def smart_fill(self, locators: List[str], text: str, timeout: int = 5000, retries: int = 2, backoff: float = 0.5):
        last_error = None

        for attempt in range(1, retries + 1):
            self.logger.info(f"Fill attempt {attempt}/{retries}")

            for index, locator in enumerate(locators, start=1):
                try:
                    self.logger.info(f"Trying fill locator #{index}: {locator}")
                    element = self.page.locator(locator).first
                    element.wait_for(state="visible", timeout=timeout)
                    element.fill(text, timeout=timeout)
                    self.logger.info(f"Fill succeeded with locator #{index}: {locator}")
                    return
                except PlaywrightTimeoutError as e:
                    last_error = e
                    self.logger.warning(f"Timeout on locator #{index}: {locator}")
                except Exception as e:
                    last_error = e
                    self.logger.warning(f"Fill failed on locator #{index}: {locator} | error={e}")

            if attempt < retries:
                sleep_time = backoff * attempt
                self.logger.info(f"Retrying fill after {sleep_time} seconds")
                time.sleep(sleep_time)

        self._take_screenshot("fill_failure")
        raise Exception(f"Could not fill any locator. locators={locators}, last_error={last_error}")