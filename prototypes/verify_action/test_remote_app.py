from __future__ import annotations

import unittest

import httpx2

from remote_app import LOCAL_HOSTS, build_app, deployment_security, mcp


class RemoteAppConfigTests(unittest.TestCase):
    def test_default_security_is_localhost_only(self):
        security = deployment_security(allowed_hosts=[], allowed_origins=[])
        self.assertTrue(security.enable_dns_rebinding_protection)
        self.assertEqual(security.allowed_hosts, LOCAL_HOSTS)

    def test_explicit_public_host_is_preserved(self):
        security = deployment_security(
            allowed_hosts=["mcp.example.com", "mcp.example.com:*"],
            allowed_origins=["https://chat.example.com"],
        )
        self.assertEqual(
            security.allowed_hosts,
            ["mcp.example.com", "mcp.example.com:*"],
        )
        self.assertEqual(security.allowed_origins, ["https://chat.example.com"])


class RemoteAppHTTPTests(unittest.IsolatedAsyncioTestCase):
    async def test_health_is_public_and_minimal(self):
        app = build_app()
        transport = httpx2.ASGITransport(app=app)
        async with httpx2.AsyncClient(
            transport=transport,
            base_url="http://localhost",
        ) as client:
            response = await client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "valta-pilot-lab",
                "mcp_path": "/mcp",
            },
        )

    async def test_unlisted_host_is_rejected_before_mcp_processing(self):
        app = build_app(
            allowed_hosts=["mcp.example.com", "mcp.example.com:*"],
            allowed_origins=[],
        )
        transport = httpx2.ASGITransport(app=app, raise_app_exceptions=False)
        async with mcp.session_manager.run():
            async with httpx2.AsyncClient(
                transport=transport,
                base_url="https://evil.example.com",
            ) as client:
                response = await client.post(
                    "/mcp",
                    json={},
                    headers={
                        "Accept": "application/json, text/event-stream",
                        "Content-Type": "application/json",
                    },
                )

        self.assertEqual(response.status_code, 421)

    async def test_configured_public_host_passes_host_gate(self):
        app = build_app(
            allowed_hosts=["mcp.example.com", "mcp.example.com:*"],
            allowed_origins=[],
        )
        transport = httpx2.ASGITransport(app=app, raise_app_exceptions=False)
        async with mcp.session_manager.run():
            async with httpx2.AsyncClient(
                transport=transport,
                base_url="https://mcp.example.com",
            ) as client:
                response = await client.post(
                    "/mcp",
                    json={},
                    headers={
                        "Accept": "application/json, text/event-stream",
                        "Content-Type": "application/json",
                    },
                )

        # The empty body is not a valid MCP request, but a configured public Host
        # must get past transport-security rather than fail with 421.
        self.assertNotEqual(response.status_code, 421)


if __name__ == "__main__":
    unittest.main()
