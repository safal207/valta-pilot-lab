from __future__ import annotations

import os

from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_server import mcp


LOCAL_HOSTS = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
LOCAL_ORIGINS = [
    "http://127.0.0.1:*",
    "http://localhost:*",
    "http://[::1]:*",
]


def _csv_env(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


def deployment_security(
    *,
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
) -> TransportSecuritySettings:
    """Build an explicit MCP transport allowlist.

    A public deployment must set VALTA_ALLOWED_HOSTS (for example
    `valta-mcp.example.com,valta-mcp.example.com:*`).  If no public host is
    configured, the service remains localhost-only instead of silently accepting
    arbitrary Host headers.
    """

    hosts = list(allowed_hosts) if allowed_hosts is not None else _csv_env("VALTA_ALLOWED_HOSTS")
    origins = (
        list(allowed_origins)
        if allowed_origins is not None
        else _csv_env("VALTA_ALLOWED_ORIGINS")
    )

    if not hosts:
        hosts = LOCAL_HOSTS.copy()
        if not origins:
            origins = LOCAL_ORIGINS.copy()

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origins,
    )


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    """Public liveness endpoint; intentionally contains no private Valta state."""

    return JSONResponse(
        {
            "status": "ok",
            "service": "valta-pilot-lab",
            "mcp_path": "/mcp",
        }
    )


def build_app(
    *,
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
):
    """Return the ASGI app hosted by uvicorn or another ASGI process manager."""

    return mcp.streamable_http_app(
        stateless_http=True,
        json_response=True,
        transport_security=deployment_security(
            allowed_hosts=allowed_hosts,
            allowed_origins=allowed_origins,
        ),
        host="0.0.0.0",
    )


app = build_app()
