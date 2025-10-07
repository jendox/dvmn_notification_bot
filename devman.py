import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any

import anyio
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger("devman_polling")

HTTPX_DEFAULT_TIMEOUT = 10.0
HTTPX_READ_TIMEOUT = 100.0
CONNECT_ERROR_SLEEP_TIMEOUT = 5.0


class Status(str, Enum):
    TIMEOUT = "timeout"
    FOUND = "found"


class Attempt(BaseModel):
    submitted_at: datetime
    is_negative: bool
    lesson_title: str
    lesson_url: str
    timestamp: float


class BaseResponse(BaseModel):
    status: Status
    request_query: list[list[Any]]


class TimeoutResponse(BaseResponse):
    timestamp_to_request: float


class FoundResponse(BaseResponse):
    new_attempts: list[Attempt] = Field(default_factory=list)
    last_attempt_timestamp: float


def get_async_client(
    base_url: str,
    api_token: str,
    default_timeout: float = HTTPX_DEFAULT_TIMEOUT,
    read_timeout: float = HTTPX_READ_TIMEOUT,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=base_url,
        headers={
            f"Authorization": f"Token {api_token}",
        },
        timeout=httpx.Timeout(default_timeout, read=read_timeout)
    )


def parse_response(data: dict[str, Any]) -> TimeoutResponse | FoundResponse:
    status = data.get("status")
    if status == Status.TIMEOUT.value:
        return TimeoutResponse(**data)
    elif status == Status.FOUND.value:
        return FoundResponse(**data)
    raise ValueError(f"Неподдерживаемый статус ответа: {status}")


async def process_response(data: dict[str, Any], queue: asyncio.Queue[Attempt]) -> float:
    response = parse_response(data)
    if response.status == Status.TIMEOUT:
        return response.timestamp_to_request
    else:
        for attempt in response.new_attempts:
            await queue.put(attempt)
        return response.last_attempt_timestamp


async def devman_long_poll(
    api_token: str,
    queue: asyncio.Queue[Attempt],
) -> None:
    try:
        timestamp: float = 0.0
        while True:
            async with get_async_client("https://dvmn.org/api", api_token) as client:
                try:
                    params = {"timestamp": timestamp} if timestamp else None
                    response = await client.get(url="/long_polling/", params=params)
                    response.raise_for_status()
                    timestamp = await process_response(response.json(), queue)
                except httpx.ReadTimeout:
                    logger.debug("httpx.ReadTimeout")
                except httpx.ConnectError:
                    logger.debug("httpx.ConnectError")
                    await anyio.sleep(CONNECT_ERROR_SLEEP_TIMEOUT)
                except (httpx.HTTPError, ValueError) as e:
                    logger.error(f"Error: {str(e)}")
    except asyncio.CancelledError:
        logger.debug("Devman long polling отменен")
    finally:
        queue.shutdown()
