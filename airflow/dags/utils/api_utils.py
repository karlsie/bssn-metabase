import json
import pandas as pd
from airflow.providers.http.hooks.http import HttpHook


def fetch_api_data(
    http_conn_id,
    endpoint,
    params=None,
    headers=None,
):
    """Fetch data from an API endpoint using Airflow HTTPHook and return as pandas DataFrame.

    Args:
        endpoint: API endpoint path (relative to the hook's base_url)
        params: Query parameters (dict)
        headers: Custom headers (dict)
        http_conn_id: Airflow HTTP connection ID (default: http_default)

    Returns:
        pd.DataFrame: Normalized data from API with lowercase column names and updated_at timestamp
    """
    try:
        print(f"Using HTTP connection ID: {http_conn_id}")
        print(
            f"Fetching data from API endpoint: {endpoint} with params: {params} and headers: {headers}"
        )
        hook = HttpHook(http_conn_id=http_conn_id, method="GET")
        response = hook.run(
            endpoint=endpoint,
            data=params,
            headers=headers,
            extra_options={"timeout": 60},
        )

        print(f"API response status: {response.status_code}")

        # Parse response if it's a string
        if isinstance(response, str):
            data = json.loads(response)
        else:
            data = response.json() if hasattr(response, "json") else response

        # Handle both dict and list responses
        rows = (
            data.get("results", [])
            if isinstance(data, dict)
            else (data if isinstance(data, list) else [])
        )
        df = pd.json_normalize(rows)

        df.columns = df.columns.str.lower().str.replace(
            r"[^a-zA-Z0-9_]", "_", regex=True
        )
        df["updated_at"] = pd.Timestamp.now()
        return df
    except Exception as e:
        raise Exception(f"Error fetching data from API: {str(e)}")
