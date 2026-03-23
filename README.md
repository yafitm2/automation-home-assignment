# Automation Home Assignment

This project implements an E2E automation flow for the Demo Web Shop site using **Python**, **Playwright**, and **Pytest**.

## Covered Flow

The automated scenario includes:

- login with an existing user
- cart cleanup before execution
- product search by query
- sorting results by price
- collecting matching items under a required max price
- paging through results when needed
- opening product URLs
- adding products to cart
- validating that cart total does not exceed the allowed budget

---

## How to Run

### Install dependencies

```powershell
pip install -r requirements.txt
playwright install
