"""Binance Futures Testnet client — handles auth, signing, and HTTP."""

import hashlib
import hmac
import os
import time
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv


class BinanceClient:
    """Lightweight, signed REST client for Binance Futures Testnet."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
    ):
        load_dotenv()
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.base_url = base_url or os.getenv(
            "BINANCE_BASE_URL", "https://testnet.binancefuture.com"
        )

        if not self.api_key or not self.api_secret:
            raise RuntimeError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env"
            )

        # Reusable HTTP session — sets the auth header once, reuses TCP connection
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ---- private helpers ----

    def _sign(self, params: dict) -> str:
        """Generate HMAC-SHA256 signature for the given params."""
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        """Send a signed HTTP request and return the parsed JSON response."""
        params = params.copy() if params else {}
        params["timestamp"] = int(time.time() * 1000)
        params["signature"] = self._sign(params)

        url = f"{self.base_url}{endpoint}"
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    # ---- public API ----

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a signed GET request."""
        return self._request("GET", endpoint, params)

    def post(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a signed POST request."""
        return self._request("POST", endpoint, params)

    def get_account(self) -> dict:
        """Fetch full account info (balances, positions, etc)."""
        return self.get("/fapi/v2/account")


if __name__ == "__main__":
    client = BinanceClient()
    account = client.get_account()
    print(f"Total wallet balance: {account.get('totalWalletBalance')} USDT")
    print(f"Available balance:    {account.get('availableBalance')} USDT")