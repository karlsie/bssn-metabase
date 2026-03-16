import requests


def list_files_in_only_office(conn_username, conn_password):
    url = "https://onlyoffice.example.com/api/files"

    response = requests.get(url, auth=(conn_username, conn_password))

    response.raise_for_status()

    files = response.json()
    print(f"Files in OnlyOffice: {len(files)} found")

    return files


def download_file_from_only_office(file, drive_url, conn_username, conn_password):
    url = f"{drive_url}/{file}"

    print(f"Downloading file from OnlyOffice: {url}")
    response = requests.get(url, auth=(conn_username, conn_password))

    response.raise_for_status()

    with open(f"/tmp/{file}", 'wb') as f:
        f.write(response.content)

    print(f"File downloaded successfully: /tmp/{file}")


def read_file_from_only_office(downloaded_file_path):
    # Placeholder for reading file content from OnlyOffice
    with open(downloaded_file_path, 'r') as f:
        content = f.read()
    print(f"File content read successfully: {downloaded_file_path}")
    return content
