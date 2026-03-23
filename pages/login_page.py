from pages.base_page import BasePage


class LoginPage(BasePage):
    LOGIN_LINK = ["a.ico-login", "a[href='/login']"]
    EMAIL_INPUT = ["input#Email", "input[name='Email']"]
    PASSWORD_INPUT = ["input#Password", "input[name='Password']"]
    LOGIN_BUTTON = ["input.login-button", "input[value='Log in']"]
    ACCOUNT_LINK = [".account", "a.account"]
    LOGIN_ERROR = [".message-error", ".validation-summary-errors"]

    def open_login_page(self):
        self.page.goto("https://demowebshop.tricentis.com/")
        self.page.wait_for_load_state("domcontentloaded")
        self.smart_click(self.LOGIN_LINK)

    def login(self, email: str, password: str):
        self.open_login_page()
        self.smart_fill(self.EMAIL_INPUT, email)
        self.smart_fill(self.PASSWORD_INPUT, password)
        self.page.wait_for_timeout(2000)
        self.smart_click(self.LOGIN_BUTTON)
        self.page.wait_for_load_state("domcontentloaded")
        self.wait_for_login_result()

    def wait_for_login_result(self, timeout: int = 5000):
        end_time = self.page.evaluate("Date.now()") + timeout

        while self.page.evaluate("Date.now()") < end_time:
            for selector in self.ACCOUNT_LINK:
                locator = self.page.locator(selector).first
                if locator.count() > 0 and locator.is_visible():
                    self.logger.info("Login success indicator found")
                    return

            for selector in self.LOGIN_ERROR:
                locator = self.page.locator(selector).first
                if locator.count() > 0 and locator.is_visible():
                    error_text = locator.inner_text().strip()
                    raise AssertionError(f"Login failed with error: {error_text}")

            self.page.wait_for_timeout(300)

        raise AssertionError("Login result was not detected within timeout.")

    def assert_login_success(self, expected_email: str):
        for selector in self.ACCOUNT_LINK:
            locator = self.page.locator(selector).first
            if locator.count() > 0 and locator.is_visible():
                locator.wait_for(state="visible", timeout=5000)
                account_text = locator.inner_text().strip()
                assert expected_email.lower() in account_text.lower(), (
                    f"Login failed. Expected account email '{expected_email}', got '{account_text}'"
                )
                return

        raise AssertionError("Login failed. Account link was not found after login.")