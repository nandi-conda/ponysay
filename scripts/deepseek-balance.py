#!/usr/bin/env python3
"""Query the DeepSeek account balance for a DeepSeek API key.

Official endpoint: GET https://api.deepseek.com/user/balance
Required header:  Authorization: Bearer <API key>

The API key is read from the DEEPSEEK_API_KEY environment variable or from
the --api-key argument. It is never printed. Prefer the environment
variable so the key does not show up in the process list.

Usage:
    DEEPSEEK_API_KEY=sk-... python3 scripts/deepseek-balance.py
    python3 scripts/deepseek-balance.py --api-key sk-...
"""

import argparse
import json
import os
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.deepseek.com"
BALANCE_PATH = "/user/balance"


def get_balance(base_url: str, api_key: str) -> dict:
    """Return the parsed JSON body of GET /user/balance."""
    url = base_url.rstrip("/") + BALANCE_PATH
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"DeepSeek balance request failed: HTTP {exc.code}\n{body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"DeepSeek balance request failed: {exc.reason}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--api-key",
        help="DeepSeek API key. Prefer the DEEPSEEK_API_KEY environment variable.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL of the DeepSeek API (default: %(default)s).",
    )
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit(
            "No DeepSeek API key found. Set DEEPSEEK_API_KEY or pass --api-key."
        )

    data = get_balance(args.base_url, api_key)

    print(f"Balance available for API calls: {data.get('is_available')}")
    for info in data.get("balance_infos", []):
        print(
            f"- {info.get('currency')}: "
            f"total {info.get('total_balance')}, "
            f"granted {info.get('granted_balance')}, "
            f"topped-up {info.get('topped_up_balance')}"
        )


if __name__ == "__main__":
    main()
