import os

import anyio
import httpx

HTTPX_DEFAULT_TIMEOUT = 10.0
HTTPX_READ_TIMEOUT = 90.0


def get_async_client(
    api_token: str,
    default_timeout: int = HTTPX_DEFAULT_TIMEOUT,
    read_timeout: int = HTTPX_READ_TIMEOUT,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url="https://dvmn.org/api",
        headers={
            f"Authorization": f"Token {api_token}",
        },
        timeout=httpx.Timeout(default_timeout, read=read_timeout)
    )


async def main():
    client = get_async_client(os.getenv("API_TOKEN"), read_timeout=5)
    timestamp: int | None = None
    while True:
        try:
            params = {"timestamp": timestamp}
            response = await client.get(url="/long_polling/", params=params)
            response.raise_for_status()
            data = response.json()
            print(f"url: {response.url} data: {data}")
            timestamp = int(data.get("timestamp_to_request"))
        except httpx.ReadTimeout:
            pass


if __name__ == "__main__":
    anyio.run(main)
