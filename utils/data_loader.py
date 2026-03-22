import json


def load_test_data(file_path="data/test_data.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
