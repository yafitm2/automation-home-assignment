import pytest

from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from utils.data_loader import load_test_data

data = load_test_data()


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

        print(
            f"Running case: {case['search_query']} | "
            f"browser={run_browser} | "
            f"max_price={case['max_price']} | "
            f"limit={case['limit']}"
        )
        login_page = LoginPage(page)

        search_page = SearchPage(page)
        product_page = ProductPage(page)
        cart_page = CartPage(page)

        assert "login_email" in user, "Missing 'login_email' in user test data"
        assert "login_password" in user, "Missing 'login_password' in user test data"

        login_page.login(user["login_email"], user["login_password"])
        login_page.assert_login_success(user["login_email"])

        cart_page.clear_cart()

        search_page.search_for_item(case["search_query"])

        product_urls = search_page.get_items_under_price(
            max_price=case["max_price"],
            target_count=case["limit"]
        )

        assert len(product_urls) > 0, f"No products found for query={case['search_query']}"

        added_items = product_page.add_items_to_cart(product_urls)

        assert len(added_items) > 0, "No items were added to the cart"

        cart_page.open_cart()
        cart_page.assert_cart_total_not_exceeds(
            budget_per_item=case["budget_per_item"],
            items_count=len(added_items)
        )
