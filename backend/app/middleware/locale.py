from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.i18n import resolve_locale


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        accept_language = request.headers.get("accept-language")
        request.state.locale = resolve_locale(accept_language)
        response = await call_next(request)
        return response
