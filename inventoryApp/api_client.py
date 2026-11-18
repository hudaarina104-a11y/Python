
import requests

BASE_URL = "http://127.0.0.1:5000"


class NetworkUnavailable(Exception):
    pass


class APIError(Exception):
    pass


def request_api(method, path, **kwargs):
    try:
        response = requests.request(
            method, BASE_URL + path,
            timeout=2, **kwargs
        )
    except (requests.ConnectionError, requests.Timeout):
        raise NetworkUnavailable("Сервер недоступний.")

    if not response.ok:
        try:
            error = response.json().get("error", response.text)
        except ValueError:
            error = response.text
        raise APIError(f"HTTP {response.status_code}: {error}")

    return response


def get_items():
    return request_api("GET", "/items").json()


def add_item(data):
    return request_api("POST", "/items", json=data).json()


def update_item(item_id, data):
    return request_api(
        "PUT", f"/items/{item_id}", json=data
    ).json()


def delete_item(item_id):
    request_api("DELETE", f"/items/{item_id}")


def export_csv():
    return request_api("GET", "/export").content
