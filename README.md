# Automation Home Assignment

This project implements an end-to-end automation flow for the Demo Web Shop website using **Python**, **Playwright**, and **Pytest**.

## Flow Covered

The automated scenario includes:

- login with an existing user
- cart cleanup before execution
- product search by query
- sorting results by price
- collecting matching items under a required max price
- paging through results when needed
- collecting product URLs
- opening product pages
- adding items to cart
- validating that cart total does not exceed the allowed budget

---

## How to Run

Install dependencies:

```powershell
pip install -r requirements.txt
playwright install

Run all tests:
pytest

Run the main E2E flow:
pytest tests/test_e2e_shopping_flow.py

Run in parallel:
pytest -n 2

Run with browser matrix:
pytest -n 2 --browser-matrix=chromium,firefox

Run with automatic Allure opening:
.\run_tests.ps1

Reporting

The project uses Allure Report.

Manual report generation:
allure generate --output allure-report --open .\allure-results

Architecture

The framework is implemented using OOP and Page Object Model.

BasePage contains shared reusable methods such as smart click, smart fill, retries, fallback locators, screenshots, and logging.
LoginPage implements the login flow.
SearchPage implements search, sorting, item extraction, logical price filtering, URL collection, and paging.
ProductPage implements product opening, option selection when needed, add-to-cart flow, and add verification.
CartPage implements cart cleanup, cart opening, total extraction, and budget validation.
test_e2e_shopping_flow.py contains the main data-driven E2E flow.