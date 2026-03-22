import re
from pages.base_page import BasePage


class CartPage(BasePage):
    ORDER_TOTAL = [
        "span.product-price.order-total strong",
        "td.cart-total-right strong"
    ]

    def open_cart(self):
        self.page.goto("https://demowebshop.tricentis.com/cart")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_url("**/cart", timeout=5000)
        self.logger.info("Opened cart page")

    def clear_cart(self):
        self.open_cart()

        remove_checkboxes = self.page.locator(
            "input[name='removefromcart'], td.remove-from-cart input[type='checkbox']"
        )
        count = remove_checkboxes.count()

        if count == 0:
            self.logger.info("Cart is already empty")
            return

        self.logger.info(f"Found {count} item(s) in cart. Removing them...")

        for i in range(count):
            checkbox = remove_checkboxes.nth(i)
            if checkbox.is_visible():
                checkbox.check()

        self.smart_click([
            "input[name='updatecart']",
            "input[value='Update shopping cart']"
        ])
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000)

        # סוגר hover / mini cart אם נשאר פתוח
        self.page.mouse.move(10, 10)

        self.logger.info("Cart cleanup completed")

    def _parse_price(self, text: str) -> float:
        cleaned = re.sub(r"[^\d.]", "", text)
        if not cleaned:
            raise ValueError(f"Could not parse price from text: {text}")
        return float(cleaned)

    def get_order_total(self) -> float:
        for locator in self.ORDER_TOTAL:
            try:
                elements = self.page.locator(locator)
                count = elements.count()

                for i in range(count):
                    element = elements.nth(i)
                    if element.is_visible():
                        text = element.inner_text().strip()
                        total = self._parse_price(text)
                        if total > 0:
                            self.logger.info(f"Order total found using locator '{locator}': {total}")
                            return total
            except Exception as e:
                self.logger.warning(f"Failed reading order total with locator '{locator}': {e}")

        raise AssertionError("Could not find order total in cart.")

    def assert_cart_total_not_exceeds(self, budget_per_item, items_count):
        allowed_total = budget_per_item * items_count
        actual_total = self.get_order_total()

        self.logger.info(f"Allowed total: {allowed_total}")
        self.logger.info(f"Actual total: {actual_total}")

        assert actual_total <= allowed_total, (
            f"Cart total exceeded allowed budget. "
            f"Actual={actual_total}, Allowed={allowed_total}"
        )