from pages.base_page import BasePage
import random
import re


class ProductPage(BasePage):
    ADD_TO_CART_BUTTON = [
        "input[id^='add-to-cart-button-']",
        "input[value='Add to cart']",
        ".add-to-cart-button"
    ]

    SUCCESS_BAR = [
        ".bar-notification.success",
        ".content",
    ]

    CART_QTY = "span.cart-qty"

    def open_product(self, url):
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")
        self.logger.info(f"Opened product page: {url}")

    def select_random_options_if_needed(self):
        try:
            selects = self.page.locator("select")
            for i in range(selects.count()):
                select = selects.nth(i)
                options = select.locator("option")
                option_count = options.count()

                if option_count > 1:
                    random_index = random.randint(1, option_count - 1)
                    value = options.nth(random_index).get_attribute("value")
                    if value:
                        select.select_option(value=value)
                        self.logger.info(f"Selected dropdown option value={value}")

            radios = self.page.locator("input[type='radio']")
            visible_enabled_radios = []

            for i in range(radios.count()):
                try:
                    radio = radios.nth(i)
                    if radio.is_visible() and radio.is_enabled():
                        visible_enabled_radios.append(radio)
                except Exception:
                    continue

            if visible_enabled_radios:
                random_radio = random.choice(visible_enabled_radios)
                random_radio.check()
                self.logger.info("Selected random radio option")

            self.logger.info("Skipping checkbox selection for safer add-to-cart flow")

        except Exception as e:
            self.logger.warning(
                f"No selectable product options found or failed selecting options: {e}"
            )

    def _extract_cart_qty(self, text: str) -> int:
        match = re.search(r"\((\d+)\)", text)
        return int(match.group(1)) if match else 0

    def _get_cart_qty(self) -> int:
        try:
            text = self.page.locator(self.CART_QTY).inner_text().strip()
            qty = self._extract_cart_qty(text)
            self.logger.info(f"Current cart qty text='{text}', parsed={qty}")
            return qty
        except Exception as e:
            self.logger.warning(f"Could not read cart quantity: {e}")
            return 0

    def _success_message_visible(self) -> bool:
        try:
            bar = self.page.locator(".bar-notification.success")
            if bar.count() > 0 and bar.first.is_visible():
                text = bar.first.inner_text().strip()
                self.logger.info(f"Success message detected: {text}")
                return "The product has been added to your shopping cart" in text
        except Exception as e:
            self.logger.warning(f"Could not read success message: {e}")
        return False

    def add_current_product_to_cart(self) -> bool:
        qty_before = self._get_cart_qty()

        self.smart_click(self.ADD_TO_CART_BUTTON)
        self.page.wait_for_timeout(2000)

        qty_after = self._get_cart_qty()
        success_visible = self._success_message_visible()

        if qty_after > qty_before or success_visible:
            self.logger.info(
                f"Add to cart verified successfully. qty_before={qty_before}, qty_after={qty_after}"
            )
            return True

        self._take_screenshot("add_to_cart_not_verified")
        self.logger.warning(
            f"Add to cart could not be verified. qty_before={qty_before}, qty_after={qty_after}"
        )
        return False

    def add_items_to_cart(self, product_urls):
        added_items = []

        for index, url in enumerate(product_urls, start=1):
            try:
                self.open_product(url)
                self.select_random_options_if_needed()

                added = self.add_current_product_to_cart()
                if added:
                    added_items.append(url)

                    safe_name = url.rstrip("/").split("/")[-1].replace("-", "_")
                    self._take_screenshot(f"product_added_{index}_{safe_name}")

                    self.logger.info(f"Product added to cart: {url}")
                else:
                    self.logger.warning(f"Product was NOT added to cart: {url}")

            except Exception as e:
                self.logger.warning(f"Failed to add product to cart: {url} | error={e}")

        return added_items
