import requests
import sys


def download_file_from_temporary_download_url(download_url, filename):
    try:
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception:
        sys.exit(1)

    print(f"Successfully downloaded dataset file to {filename}")


def main():
    # Parameters
    base_url = "https://api.dataplatform.knmi.nl/open-data/v1"
    api_key = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImE3NDdjMjVjMWRlNTQ3ZjdhMjM3ZmM5MmM0ZDBiNTkxIiwiaCI6Im11cm11cjEyOCJ9"
    dataset_name = "SVF_NL"
    dataset_version = "3"

    files = [
        "37EZ2.tif",
        "37FZ1.tif",
        "37FZ2.tif",
        "37GN2.tif",
        "37HN1.tif",
        "37HN2.tif",
    ]

    for filename in files:
        filename = filename.lower()
        filename = "SVF_r" + filename

        # get temporary download url
        endpoint = f"{base_url}/datasets/{dataset_name}/versions/{dataset_version}/files/{filename}/url"
        print(endpoint)
        get_file_response = requests.get(endpoint, headers={"Authorization": api_key})
        j = get_file_response.json()
        url = j['temporaryDownloadUrl']

        # with the url download the file
        download_file_from_temporary_download_url(url, filename)


if __name__ == "__main__":
    main()
