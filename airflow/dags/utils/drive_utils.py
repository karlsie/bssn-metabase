import requests
import pandas as pd
from datetime import datetime


def download_file_from_only_office(file_url, filename, token, password):
    print(f"Downloading file from URL: {file_url}")
    response = requests.get(file_url, auth=(token, password))

    response.raise_for_status()

    with open(f"/tmp/{filename}", "wb") as f:
        f.write(response.content)

    print(f"File downloaded successfully: /tmp/{filename}")


def read_file_from_only_office(downloaded_file_path, format):
    """Read CSV, XLSX, or XLS files based on format parameter and add created_at timestamp."""
    format = format.lower()

    if format == "csv":
        df = pd.read_csv(downloaded_file_path)
    elif format in ("xlsx", "xls"):
        df = pd.read_excel(downloaded_file_path)
    else:
        raise ValueError(
            f"Unsupported file format: {format}. Supported: csv, xlsx, xls"
        )

    # Add created_at timestamp
    df["created_at"] = datetime.now()

    print(df.columns)

    print(f"File read successfully: {downloaded_file_path}")
    return df
