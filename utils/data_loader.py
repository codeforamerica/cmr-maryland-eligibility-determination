import pandas as pd


def load_example_data():
    try:
        return {
            name: pd.read_csv(f"data/{name}.csv")
            for name in ["parties", "cases", "charges"]
        }
    except Exception as e:
        print(f"Error loading example data: {e}")
        return {}


EXAMPLE_DATA = load_example_data()
