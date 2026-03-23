import re
from pages.base_page import BasePage


class SearchPage(BasePage):
    BASE_URL = "https://demowebshop.tricentis.com"

    SEARCH_INPUT = [
        "input#small-searchterms",
        "input[name='q']",
    ]

    SEARCH_BTN = [
        "input.search-box-button",
        "input[value='Search']",
    ]

    SORT_DROPDOWN = [
        "select#products-orderby",
        "select[name='products-orderby']",
    ]

    PRODUCT_CARDS = [
        ".item-box",
        ".product-item",
    ]

    PRODUCT_LINK = [
        "h2.product-title a",
        ".product-title a",
    ]

    PRODUCT_PRICE = [
        ".prices .actual-price",
        ".actual-price",
    ]

    NEXT_PAGE_LINK = [
        ".pager li.next-page a",
        ".pager .next-page a",
    ]

    def search_for_item(self, item_name: str):
        self.page.goto(self.BASE_URL)
        self.page.wait_for_load_state("domcontentloaded")
        self.smart_fill(self.SEARCH_INPUT, item_name)
        self.smart_click(self.SEARCH_BTN)
        self.page.wait_for_load_state("domcontentloaded")

    def sort_by_price_low_to_high(self):
        self.select_dropdown_by_text(self.SORT_DROPDOWN, "Price: Low to High")
        self.page.wait_for_load_state("domcontentloaded")
        self.logger.info("Sorted results by price: Low to High")

    def _parse_price(self, price_text: str) -> float:
        cleaned = re.sub(r"[^\d.]", "", price_text)
        return float(cleaned) if cleaned else 0.0

    def _get_cards_locator(self):
        for locator in self.PRODUCT_CARDS:
            cards = self.page.locator(locator)
            if cards.count() > 0:
                self.logger.info(f"Using product cards locator: {locator}")
                return cards
        raise AssertionError("No product cards found.")

    def _get_first_existing_locator(self, parent, locators):
        for locator in locators:
            element = parent.locator(locator).first
            if element.count() > 0:
                return element
        raise AssertionError(f"No matching locator found from: {locators}")

    def _click_next_page(self):
        for locator in self.NEXT_PAGE_LINK:
            try:
                next_btn = self.page.locator(locator).first
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    self.page.wait_for_load_state("domcontentloaded")
                    self.logger.info(f"Moved to next page using locator: {locator}")
                    return True
            except Exception:
                continue
        return False

    def _extract_item_data(self, card):
        link_element = self._get_first_existing_locator(card, self.PRODUCT_LINK)
        price_element = self._get_first_existing_locator(card, self.PRODUCT_PRICE)

        title = link_element.inner_text().strip()
        href = link_element.get_attribute("href")
        price = self._parse_price(price_element.inner_text().strip())

        if not href:
            return None

        full_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

        return {
            "title": title,
            "price": price,
            "url": full_url,
        }

    def _is_matching_item(self, item, search_query, max_price):
        text_to_check = f"{item['title']} {item['url']}".lower()
        return search_query in text_to_check and item["price"] <= max_price

    def get_matching_items(self, search_query, max_price, target_count):
        found_items = []
        seen_urls = set()
        search_query = search_query.lower()

        while len(found_items) < target_count:
            cards = self._get_cards_locator()

            for i in range(cards.count()):
                try:
                    item = self._extract_item_data(cards.nth(i))
                    if not item or item["url"] in seen_urls:
                        continue

                    if self._is_matching_item(item, search_query, max_price):
                        found_items.append(item)
                        seen_urls.add(item["url"])
                        self.logger.info(
                            f"Matched product: title='{item['title']}', "
                            f"price={item['price']}, url={item['url']}"
                        )

                    if len(found_items) >= target_count:
                        break

                except Exception as e:
                    self.logger.warning(f"Failed reading product #{i + 1}: {e}")

            if len(found_items) >= target_count or not self._click_next_page():
                if len(found_items) < target_count:
                    self.logger.info("No more pages or matching products.")
                break

        return found_items

    def search_items_by_name_under_price(self, query: str, max_price: float, limit: int = 5):
        self.search_for_item(query)
        self.sort_by_price_low_to_high()
        items = self.get_matching_items(query, max_price, limit)
        return [item["url"] for item in items]