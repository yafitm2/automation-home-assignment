import pytest

from tests.base_test import BaseTest
from pages.search_page import SearchPage
from utils.data_loader import load_test_data


data = load_test_data()


class TestSearch(BaseTest):

    @pytest.mark.parametrize("case", data["test_cases"])
    def test_search_items_under_price(self, case):
        search_page = SearchPage(self.page)

        search_page.search_for_item(case["search_query"])
        results = search_page.get_items_under_price(
            max_price=case["max_price"],
            target_count=case["limit"]
        )

        print("Found items:", results)

        assert len(results) > 0, f"No products found under the requested price for query={case['search_query']}"
        assert len(results) <= case["limit"], "Returned more items than requested"
        assert all(url.startswith(data["base_url"]) for url in results), "Invalid product URL returned"