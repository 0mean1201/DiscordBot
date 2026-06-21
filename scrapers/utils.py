import ssl
import urllib3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GachonNotifyBot/1.0)"
}


class LegacySSLAdapter(HTTPAdapter):
    """구형 SSL 암호화를 사용하는 서버(gachon.ac.kr)를 위한 어댑터."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = ctx
        super().init_poolmanager(*args, **kwargs)


def get(url, params=None):
    session = requests.Session()
    session.mount("https://", LegacySSLAdapter())
    return session.get(url, params=params, headers=HEADERS, timeout=15, verify=False)
