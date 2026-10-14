"""Compose optional OAuth routes without changing the legacy application's middleware."""

from contextlib import AsyncExitStack, asynccontextmanager

from starlette.applications import Starlette
from starlette.routing import Mount, Route

from tickdb_mcp.config import settings
from tickdb_mcp.middleware import AuthMiddleware
from tickdb_mcp.server import create_mcp


def create_http_app():
    legacy = create_mcp().streamable_http_app()
    if not settings.oauth_enabled:
        return AuthMiddleware(legacy)

    from tickdb_mcp.oauth import create_oauth_app

    oauth, oauth_app = create_oauth_app(settings)

    @asynccontextmanager
    async def lifespan(app):
        async with AsyncExitStack() as stack:
            await stack.enter_async_context(legacy.router.lifespan_context(legacy))
            await stack.enter_async_context(oauth_app.router.lifespan_context(oauth_app))
            yield

    routes = [Route(route.path, endpoint=oauth) for route in oauth_app.routes]
    routes.append(Mount("/", app=AuthMiddleware(legacy)))
    return Starlette(routes=routes, lifespan=lifespan)
