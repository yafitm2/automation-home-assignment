import pytest

from pages.search_page import SearchPage
from utils.data_loader import load_test_data

data = load_test_data()


class TestSearch:

    @pytest.mark.parametrize(
        "case",
        data["test_cases"],
        ids=[f"chromium-case{i}" for i, _ in enumerate(data["test_cases"])]
    )
    def test_search_items_under_price(self, page, case):
        search_page = SearchPage(page)

        search_page.search_for_item(case["search_query"])
        search_page.sort_by_price_low_to_high()

        items = search_page.get_matching_items(
            search_query=case["search_query"],
            max_price=case["max_price"],
            target_count=case["limit"]
        )

        assert len(items) > 0, f"No matching products found for query={case['search_query']}"
        assert len(items) <= case["limit"], f"Returned more than limit for query={case['search_query']}"

        for item in items:
            text_to_check = f"{item['title']} {item['url']}".lower()

            assert case["search_query"].lower() in text_to_check, (
                f"Item is not relevant to query '{case['search_query']}': {item}"
            )

            assert item["price"] <= case["max_price"], (
                f"Item price exceeds max_price={case['max_price']}: {item}"
            )