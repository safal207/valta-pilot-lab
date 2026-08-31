# Stellar Kraal issue #94 validation

Upstream commit: `cca5f033318f43cb9b18060d161873d75df58381`

Validated in GitHub Actions:

- `cargo fmt -p stellarkraal -- --check` — PASS
- `cargo test -p stellarkraal` — PASS
- `cargo clippy -p stellarkraal --all-targets -- -D warnings` — PASS
- release WASM build — PASS

The patch adds a checked monotonic instance nonce to `open_loan`, a
same-ledger close/reopen regression, and generated snapshot updates.
