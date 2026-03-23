import pytest
import allure

from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from utils.data_loader import load_test_data

data = load_test_data()


@allure.epic("E2E Shopping Flow")
@allure.feature("Search, Add to Cart, and Budget Validation")
class TestShoppingFlow:

    @pytest.mark.parametrize(
        "case",
        data["test_cases"],
        ids=[
            f"case{i}-{case['search_query']}"
            for i, case in enumerate(data["test_cases"], start=1)
        ]
    )
    def test_search_add_to_cart_and_validate_budget(self, page, run_browser, case):
        user = data["user"]

        allure.dynamic.title(
            f"Shopping flow | browser={run_browser} | query={case['search_query']} | max_price={case['max_price']}"
        )
        allure.dynamic.description(
            "Validate end-to-end shopping flow: login, search, collect matching items, add to cart, and verify cart total does not exceed budget."
        )
        allure.dynamic.tag(run_browser)

        with allure.step("Initialize page objects"):
            login_page = LoginPage(page)
            search_page = SearchPage(page)
            product_page = ProductPage(page)
            cart_page = CartPage(page)

        with allure.step("Validate user test data"):
            assert "login_email" in user, "Missing 'login_email' in user test data"
            assert "login_password" in user, "Missing 'login_password' in user test data"

        with allure.step("Attach current test data"):
            allure.attach(
                user["login_email"],
                name="login_email",
                attachment_type=allure.attachment_type.TEXT
            )
            allure.attach(
                str(case),
                name="test_case",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Login with valid user"):
            login_page.login(user["login_email"], user["login_password"])
            login_page.assert_login_success(user["login_email"])
            page.wait_for_timeout(2000)

        with allure.step("Clear cart before test"):
            cart_page.clear_cart()

        with allure.step(f"Search for item: {case['search_query']}"):
            search_page.search_for_item(case["search_query"])
            search_page.sort_by_price_low_to_high()
            page.wait_for_timeout(2000)

        with allure.step("Collect matching items under max price"):
            items = search_page.get_matching_items(
                search_query=case["search_query"],
                max_price=case["max_price"],
                target_count=case["limit"]
            )

            assert len(items) <= case["limit"], (
                f"Returned more than limit for query={case['search_query']}"
            )

            allure.attach(
                str(items),
                name="matching_items",
                attachment_type=allure.attachment_type.TEXT
            )

            if len(items) == 0:
                pytest.skip(
                    f"No matching products found for query={case['search_query']}. "
                    f"This is a valid search result, but cart flow cannot continue."
                )

        with allure.step("Validate each returned item relevance and price"):
            for index, item in enumerate(items, start=1):
                with allure.step(f"Validate item #{index}: {item['title']}"):
                    text_to_check = f"{item['title']} {item['url']}".lower()

                    assert case["search_query"].lower() in text_to_check, (
                        f"Item is not relevant to query '{case['search_query']}': {item}"
                    )
                    assert item["price"] <= case["max_price"], (
                        f"Item price exceeds max_price={case['max_price']}: {item}"
                    )

        with allure.step("Add matching items to cart"):
            product_urls = [item["url"] for item in items]

            allure.attach(
                "\n".join(product_urls),
                name="product_urls",
                attachment_type=allure.attachment_type.TEXT
            )

            added_items = product_page.add_items_to_cart(product_urls)

            assert len(added_items) > 0, "No items were added to the cart"

            allure.attach(
                str(added_items),
                name="added_items",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validate cart total against budget"):
            cart_page.open_cart()
            cart_page.assert_cart_total_not_exceeds(
                budget_per_item=case["budget_per_item"],
                items_count=len(added_items)
            )