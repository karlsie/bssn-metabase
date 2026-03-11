import requests
import pandas as pd


def fetch_api_data(url, params=None, headers=None):
    """Fetch data from an API endpoint and return as a pandas DataFrame."""
    try:
        response = requests.get(url, params=params, headers=headers, timeout=60)
        response.raise_for_status()  # Raise an error for bad status codes

        data = response.json()
        rows = data.get("results", [])
        df = pd.json_normalize(rows)

        df.columns = df.columns.str.lower().str.replace(
            r"[^a-zA-Z0-9_]", "_", regex=True
        )
        df["updated_at"] = pd.Timestamp.now()
        return df
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data from API: {str(e)}")
