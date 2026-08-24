# Remote MCP deployment

Prototype 003 turns the Valta verifier into a deployment-ready ASGI service.

## Endpoints

- `GET /health` — public liveness only.
- `/mcp` — MCP v2 Streamable HTTP endpoint with JSON responses.

The ASGI object is:

```text
prototypes/verify_action/remote_app.py:app
```

## Required production-host configuration

The MCP SDK protects Streamable HTTP against DNS rebinding. A service deployed behind a real hostname must explicitly allow that Host header.

Set `VALTA_ALLOWED_HOSTS` to a comma-separated allowlist. Include both the bare hostname and the optional-port form when appropriate:

```bash
VALTA_ALLOWED_HOSTS=valta-mcp.example.com,valta-mcp.example.com:*
```

Browser-based MCP clients that send an `Origin` header must also be allowlisted explicitly:

```bash
VALTA_ALLOWED_ORIGINS=https://app.example.com
```

If `VALTA_ALLOWED_HOSTS` is absent or empty, the service deliberately remains localhost-only. This is fail-closed behavior, not a deployment convenience.

## Container

From the repository root:

```bash
docker build -t valta-pilot-lab -f prototypes/verify_action/Dockerfile .
docker run --rm -p 8000:8000 valta-pilot-lab
```

Local checks:

```bash
curl http://127.0.0.1:8000/health
```

For a real hostname, the hosting platform or reverse proxy should terminate HTTPS and forward traffic to the container. The container listens on `0.0.0.0:${PORT:-8000}`.

Example environment for a deployed host:

```bash
VALTA_ALLOWED_HOSTS=valta-mcp.example.com,valta-mcp.example.com:*
PORT=8000
```

The remote MCP URL is then:

```text
https://valta-mcp.example.com/mcp
```

## Security boundary

Prototype 003 is remotely callable but is **not production payment infrastructure**.

Current intentional limitations:

- no user/account authentication yet;
- caller supplies the prototype policy snapshot;
- duplicate state is process-local memory;
- no wallet keys or payment execution are present;
- `ALLOW` proves a policy decision, not downstream execution;
- no private customer data should be placed in this public prototype.

Before real financial use, replace caller-supplied policy and in-memory duplicate state with authenticated, durable Valta state and add authorization for the MCP endpoint.

## CI gate

`Prototype 003 Remote MCP` must prove:

1. all existing verifier/MCP tests still pass;
2. `/health` returns `200`;
3. an unlisted Host is rejected with `421`;
4. an explicitly configured Host passes the transport-security gate;
5. the Docker image builds and boots successfully.
