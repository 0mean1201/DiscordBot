import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GachonNotifyBot/1.0)"
}


def get(url, params=None):
    return requests.get(url, params=params, headers=HEADERS, timeout=15, verify=False)
