import re
from pages.base_page import BasePage


class CartPage(BasePage):
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

    def get_cart_items_count(self) -> int:
        possible_rows = [
            "table.cart tbody tr",
            ".cart-item-row",
            "tr.cart-item-row"
        ]

        for locator in possible_rows:
            try:
                rows = self.page.locator(locator)
                count = rows.count()
                if count > 0:
                    self.logger.info(f"Cart items found using '{locator}': {count}")
                    return count
            except Exception as e:
                self.logger.warning(f"Failed checking cart rows with '{locator}': {e}")

        self.logger.info("No cart items found")
        return 0

    def get_order_total(self) -> float:
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)

        possible_locators = [
            ".cart-total .order-total strong",
            ".cart-total .product-price",
            ".order-total strong",
            "td.cart-total-right strong",
            ".totals strong",
            ".cart-total td",
        ]

        for locator in possible_locators:
            try:
                elements = self.page.locator(locator)
                count = elements.count()
                self.logger.info(f"Trying total locator '{locator}', found {count} element(s)")

                for i in range(count):
                    element = elements.nth(i)
                    if element.is_visible():
                        text = element.inner_text().strip()
                        self.logger.info(f"Total candidate text: '{text}'")

                        try:
                            total = self._parse_price(text)
                            if total > 0:
                                self.logger.info(
                                    f"Order total found using locator '{locator}': {total}"
                                )
                                return total
                        except Exception as parse_error:
                            self.logger.warning(
                                f"Could not parse price from '{text}': {parse_error}"
                            )

            except Exception as e:
                self.logger.warning(f"Failed reading total with locator '{locator}': {e}")

        self._take_screenshot("cart_total_not_found")
        body_text = self.page.locator("body").inner_text()
        self.logger.info(f"Cart page text preview: {body_text[:2000]}")

        raise AssertionError("Could not find order total in cart.")

    def assert_cart_total_not_exceeds(self, budget_per_item, items_count):
        actual_items = self.get_cart_items_count()
        assert actual_items > 0, "Cart is empty after adding product"

        allowed_total = budget_per_item * items_count
        actual_total = self.get_order_total()

        self.logger.info(f"Allowed total: {allowed_total}")
        self.logger.info(f"Actual total: {actual_total}")

        self._take_screenshot("cart_page_budget_validation")

        assert actual_total <= allowed_total, (
            f"Cart total exceeded allowed budget. "
            f"Actual={actual_total}, Allowed={allowed_total}"
        )
