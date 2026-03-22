from pages.base_page import BasePage
import random

class ProductPage(BasePage):
    ADD_TO_CART_BUTTON = [
        "input#add-to-cart-button-13",
        "input[value='Add to cart']",
        ".add-to-cart-button"
    ]

    def open_product(self, url):
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
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
            if radios.count() > 0:
                random_index = random.randint(0, radios.count() - 1)
                radios.nth(random_index).check()
                self.logger.info("Selected random radio option")

            checkboxes = self.page.locator("input[type='checkbox']")
            for i in range(checkboxes.count()):
                try:
                    checkboxes.nth(i).check()
                    self.logger.info(f"Checked checkbox #{i + 1}")
                except Exception:
                    continue

        except Exception as e:
            self.logger.warning(f"No selectable product options found or failed selecting options: {e}")

    def add_current_product_to_cart(self):
        self.smart_click(self.ADD_TO_CART_BUTTON)
        self.page.wait_for_load_state("networkidle")
        self.logger.info("Clicked Add to cart")

    def add_items_to_cart(self, product_urls):
        added_items = []

        for url in product_urls:
            try:
                self.open_product(url)
                self.select_random_options_if_needed()
                self.add_current_product_to_cart()
                added_items.append(url)
                self.logger.info(f"Product added to cart: {url}")
            except Exception as e:
                self.logger.warning(f"Failed to add product to cart: {url} | error={e}")

        return added_items