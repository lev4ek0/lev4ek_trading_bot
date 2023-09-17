from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from prometheus_client import Counter

ok_rps = Counter('ok_rps', 'Ok rps counter')
bad_rps = Counter('bad_rps', 'Bad rps counter')


class MetricsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        try:
            result = await handler(event, data)
            ok_rps.inc()
        except Exception as e:
            bad_rps.inc()
            raise
        return result
