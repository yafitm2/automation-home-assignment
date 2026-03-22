import re
from pages.base_page import BasePage


class SearchPage(BasePage):
    BASE_URL = "https://demowebshop.tricentis.com"

    SEARCH_INPUT = [
        "input#small-searchterms",
        "input[name='q']"
    ]

    SEARCH_BTN = [
        "input.search-box-button",
        "input[value='Search']"
    ]

    PRODUCT_CARDS = [
        ".item-box",
        ".product-item"
    ]

    PRODUCT_LINK = [
        "h2.product-title a",
        ".product-title a"
    ]

    PRODUCT_PRICE = [
        ".prices .actual-price",
        ".actual-price"
    ]

    NEXT_PAGE_LINK = [
        ".pager li.next-page a",
        ".pager .next-page a"
    ]

    def search_for_item(self, item_name: str):
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        self.page.mouse.move(10, 10)
        self.smart_fill(self.SEARCH_INPUT, item_name)
        self.smart_click(self.SEARCH_BTN)
        self.page.wait_for_load_state("networkidle")

    def _parse_price(self, price_text: str) -> float:
        cleaned = re.sub(r"[^\d.]", "", price_text)
        return float(cleaned) if cleaned else 0.0

    def _get_cards_locator(self):
        for locator in self.PRODUCT_CARDS:
            cards = self.page.locator(locator)
            if cards.count() > 0:
                self.logger.info(f"Using product cards locator: {locator}")
                return cards
        raise AssertionError("No product cards were found using fallback locators.")

    def _get_first_existing_locator(self, parent, locators):
        for locator in locators:
            candidate = parent.locator(locator).first
            if candidate.count() > 0:
                return candidate
        raise AssertionError(f"No matching locator found from: {locators}")

    def _click_next_page(self):
        for locator in self.NEXT_PAGE_LINK:
            try:
                next_btn = self.page.locator(locator).first
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    self.page.wait_for_load_state("networkidle")
                    return True
            except Exception:
                continue
        return False

    def get_items_under_price(self, max_price, target_count):
        found_items = []
        seen_urls = set()

        while len(found_items) < target_count:
            cards = self._get_cards_locator()
            cards_count = cards.count()

            for i in range(cards_count):
                card = cards.nth(i)

                try:
                    link_element = self._get_first_existing_locator(card, self.PRODUCT_LINK)
                    price_element = self._get_first_existing_locator(card, self.PRODUCT_PRICE)

                    title = link_element.inner_text().strip()
                    href = link_element.get_attribute("href")
                    price_text = price_element.inner_text().strip()
                    price = self._parse_price(price_text)

                    if price <= max_price and href:
                        full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

                        if full_url not in seen_urls:
                            self.logger.info(
                                f"Matched product: title='{title}', price={price}, url={full_url}"
                            )
                            found_items.append(full_url)
                            seen_urls.add(full_url)

                    if len(found_items) >= target_count:
                        break

                except Exception as e:
                    self.logger.warning(f"בעיה בקריאת מוצר #{i}: {e}")

            if len(found_items) >= target_count:
                break

            if not self._click_next_page():
                self.logger.info("אין יותר עמודים או מוצרים מתאימים.")
                break

        return found_items