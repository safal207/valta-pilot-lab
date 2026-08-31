from __future__ import annotations

import sys
from pathlib import Path


root = Path(sys.argv[1])
lib_path = root / "contracts/stellarkraal/src/lib.rs"
test_path = root / "contracts/stellarkraal/tests/lifecycle_simulation.rs"

lib = lib_path.read_text(encoding="utf-8")
config_decl = 'const CONFIG: Symbol = symbol_short!("CONFIG");\n'
config_replacement = (
    config_decl + 'const LOAN_NONCE: Symbol = symbol_short!("LNONCE");\n'
)
if lib.count(config_decl) != 1:
    raise SystemExit("expected exactly one CONFIG declaration")
lib = lib.replace(config_decl, config_replacement, 1)

seed_block = "\n".join(
    [
        "        let mut seed = soroban_sdk::Bytes::new(&e);",
        "        for b in now.to_be_bytes() {",
        "            seed.push_back(b);",
        "        }",
        "        // mix in asset_id bytes for uniqueness",
        "        for b in asset_id.to_array() {",
        "            seed.push_back(b);",
        "        }",
        "        let loan_id: BytesN<32> = e.crypto().sha256(&seed).into();",
    ]
)
replacement = "\n".join(
    [
        "        let loan_nonce: u64 = e.storage().instance().get(&LOAN_NONCE).unwrap_or(0);",
        "        let next_loan_nonce = loan_nonce",
        "            .checked_add(1)",
        "            .ok_or(Error::ArithmeticError)?;",
        "        e.storage().instance().set(&LOAN_NONCE, &next_loan_nonce);",
        "",
        "        let mut seed = soroban_sdk::Bytes::new(&e);",
        "        for b in now.to_be_bytes() {",
        "            seed.push_back(b);",
        "        }",
        "        for b in asset_id.to_array() {",
        "            seed.push_back(b);",
        "        }",
        "        for b in next_loan_nonce.to_be_bytes() {",
        "            seed.push_back(b);",
        "        }",
        "        let loan_id: BytesN<32> = e.crypto().sha256(&seed).into();",
    ]
)
if lib.count(seed_block) != 1:
    raise SystemExit("expected exactly one open_loan seed block")
lib_path.write_text(lib.replace(seed_block, replacement, 1), encoding="utf-8")

tests = test_path.read_text(encoding="utf-8")
if "fn scenario_same_ledger_reopen_preserves_closed_loan" in tests:
    raise SystemExit("regression test already exists")
scenario_line = (
    '//! 6. `scenario_partial_oracle_recovery_after_staleness` — partial quorum\n'
)
if tests.count(scenario_line) != 1:
    raise SystemExit("expected lifecycle scenario list entry")
tests = tests.replace(
    scenario_line,
    scenario_line
    + '//! 7. `scenario_same_ledger_reopen_preserves_closed_loan` — loan ID collision regression\n',
    1,
)
regression = r'''

// ── Scenario 7: same-ledger reopen identity ────────────────────────────────

/// Closing and reopening a loan for the same asset without advancing the
/// ledger must create a fresh ID and preserve the first closed loan record.
#[test]
fn scenario_same_ledger_reopen_preserves_closed_loan() {
    let sim = Sim::boot();
    let (client, actors) = (&sim.client, &sim.actors);

    let asset_id = client.register_asset(
        &actors.farmer_a,
        &symbol_short!("CATTLE"),
        &symbol_short!("KR006"),
        &1_000_000,
    );
    let ledger_sequence = sim.env.ledger().sequence();

    let first_loan_id = client.open_loan(&actors.farmer_a, &asset_id, &500_000);
    let first_open = client.get_loan(&first_loan_id);
    assert_eq!(first_open.opened_at, ledger_sequence);

    assert_eq!(
        client.repay_loan(&actors.farmer_a, &first_loan_id, &first_open.balance),
        0
    );
    let first_closed = client.get_loan(&first_loan_id);
    assert!(!first_closed.active);
    assert_eq!(first_closed.balance, 0);
    assert!(!client.get_asset(&asset_id).on_loan);

    let second_loan_id = client.open_loan(&actors.farmer_a, &asset_id, &500_000);

    assert_eq!(sim.env.ledger().sequence(), ledger_sequence);
    assert_ne!(first_loan_id, second_loan_id);

    let first_after_reopen = client.get_loan(&first_loan_id);
    assert!(!first_after_reopen.active);
    assert_eq!(first_after_reopen.balance, 0);
    assert_eq!(first_after_reopen.principal, first_closed.principal);
    assert_eq!(first_after_reopen.borrower, first_closed.borrower);
    assert_eq!(first_after_reopen.asset_id, first_closed.asset_id);
    assert_eq!(first_after_reopen.opened_at, first_closed.opened_at);
    assert_eq!(first_after_reopen.updated_at, first_closed.updated_at);

    let second = client.get_loan(&second_loan_id);
    assert!(second.active);
    assert_eq!(second.opened_at, ledger_sequence);
    assert_eq!(second.asset_id, asset_id);
    assert!(client.get_asset(&asset_id).on_loan);
}
'''
test_path.write_text(tests.rstrip() + regression + "\n", encoding="utf-8")
