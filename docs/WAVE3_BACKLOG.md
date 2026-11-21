<!-- GENERATED FILE — do not hand-edit.
     Source of truth is the matching docs/WAVE<N>_BACKLOG.json.
     Regenerate with: python3 scripts/render_wave_backlog_md.py <path-to-json> -->

# Wave backlog

**140 issues, 25000 points** — 110 high (200 pts each), 30 low (100 pts each).

By repo: `sorocharge-core` (109), `sorocharge-php` (31)

By area: `ci-release` (17), `mpp` (30), `signer` (61), `x402` (32)

Every item below cites a specific file and gap found by reading the repositories during this wave's survey, not a generic roadmap item. Complexity labels were assigned to hit an exact point quota per explicit maintainer instruction — they do not all correspond to real relative effort size.

## High — 200 points (110)

### fix: re-track cargo-semver-checks CI integration — closed as completed, never actually added

`repo:sorocharge-core` `area:ci-release`

**Description.** sorocharge-core#27 ('chore: add cargo-semver-checks to CI ahead of future crates.io publishes') was closed by the Wave bot as completed, attributed to a PR. .github/workflows/ci.yml has no semver-checks step, no cargo-semver-checks install, nothing matching this at all.

**Why.** A closed-as-completed issue with no corresponding implementation is exactly the kind of overclaim that erodes trust in the Wave backlog's own closure signal — found by checking the claim against the actual repo state, not by trusting the bot. If this one slipped through, the next audit item (auditing other closures) matters more, not less.

**Acceptance criteria.**
- [ ] A CI job (or documented pre-publish step) actually runs cargo-semver-checks against the last published version, matching #27's original acceptance criteria
- [ ] The PR that resolves this links back to #27 and states plainly that the prior closure didn't reflect real work
- [ ] cargo fmt/clippy/test/deny all still pass

**Guidance.**
- .github/workflows/ci.yml — grep for 'semver' to confirm it's genuinely absent before starting
- sorocharge-core#27's original acceptance criteria are still the right bar

### chore: audit every Wave 2 issue closed as "completed" against the actual repo state

`repo:sorocharge-core` `area:ci-release`

**Description.** #27 was closed as completed with zero corresponding implementation. A spot-check of a handful of other closures (THREAT_MODEL.md, deny.toml, benches/, fuzz/ targets) found those genuinely done — but #27 proves the Wave bot's auto-closure isn't a reliable signal on its own, and a full audit hasn't been done.

**Why.** 127 of 159 Wave 1+2 issues are closed. If even one more has the same gap as #27, it's sitting unnoticed exactly the way #27 was until this session specifically went looking.

**Acceptance criteria.**
- [ ] Every closed issue is checked against the actual repo state: does the claimed file/behavior genuinely exist, not just "a PR referenced this title"
- [ ] Any other false-completion found is reported with the same specificity as this issue's own description of #27, and either fixed or re-opened
- [ ] A short written finding lists what was checked and the result, even if the answer is "no other false completions found"

**Guidance.**
- gh issue list --repo sorocharge/sorocharge-core --state closed — the full list to check
- sorocharge-core#27 is the known example and the template for what counts as a real discrepancy

### test: scripts/malware_scan.py has zero automated test coverage

`repo:sorocharge-core` `area:ci-release`

**Description.** The malware/supply-chain scanner that gates every PR (required via branch protection) was verified ad hoc during development — run once against synthetic malicious content in a scratch directory, never committed as a repeatable test. There is no tests/ file for it anywhere.

**Why.** A scanner that silently stops catching what it's supposed to catch (a regex typo, a refactor that breaks the self-exclusion path, an IOC accidentally deleted from the JSON) would only be noticed the next time someone manually re-verifies it by hand — which is exactly how it was built in the first place, and exactly the gap this issue closes.

**Acceptance criteria.**
- [ ] A test harness (e.g. constructing a temp git repo, or a fixtures/ directory of synthetic malicious files) exercises every check category: a known IOC string, a malicious npm/Packagist package name, a suspicious filename/extension, an unallowlisted exec-pattern call, a long encoded blob, a high-entropy long line
- [ ] A test confirms the protected-files guard fires when security/malware_iocs.json or security/scan_allowlist.json itself is touched
- [ ] A test confirms a file in security/scan_allowlist.json is correctly exempted from the exec-pattern check
- [ ] These tests run in CI (can be a new step in the malware-scan job, or a separate fast job)

**Guidance.**
- scripts/malware_scan.py's own module docstring and PROTECTED_FILES/EXEC_PATTERNS for what to exercise
- Python's unittest or pytest both work; no new dependency is needed for something this scoped — stdlib unittest is enough

### perf: add criterion benchmarks for Facilitator and MppServer's non-RPC verification logic

`repo:sorocharge-core` `area:ci-release`

**Description.** benches/signer_benchmarks.rs covers build_charge_entry/sign_entry/verify_entry, but nothing benchmarks the facilitator/server-side logic that doesn't require network I/O: parse_payment_transaction, verify_transfer_effects against a fixed simulation payload, the safety checks inside Facilitator::validate / MppServer's credential validation.

**Why.** This is exactly the code path a production facilitator/server calls on every single incoming payment — its own latency matters independently of RPC round-trip time, and there's currently no baseline for it at all.

**Acceptance criteria.**
- [ ] benches/facilitator_benchmarks.rs (or similarly named) covers parse_payment_transaction for both x402 and mpp, and verify_transfer_effects, using fixed fixture inputs (no live RPC)
- [ ] cargo bench runs successfully
- [ ] A baseline result is recorded in the PR description

**Guidance.**
- benches/signer_benchmarks.rs is the existing pattern to follow
- crates/sorocharge-x402/src/facilitator.rs's validate(), crates/sorocharge-mpp/src/server.rs's settle_credential() for what's RPC-bound vs pure-computation — only benchmark the latter

### ci: wire up cargo-mutants (mutation testing)

`repo:sorocharge-core` `area:ci-release`

**Description.** .gitignore already has a stanza for cargo-mutants output ('Generated by cargo mutants'), suggesting someone considered it, but it was never actually added to CI or run.

**Why.** This project's whole verification posture is built on 'tests prove behavior, not just coverage' — golden vectors, fuzz targets, property tests. Mutation testing is the natural next layer: it proves the existing tests would actually catch a real behavioral change, not just that lines got executed.

**Acceptance criteria.**
- [ ] cargo-mutants runs against at least sorocharge-signer (the highest-stakes crate) in CI, on a schedule (like fuzz) rather than blocking every PR given its runtime
- [ ] Surviving mutants are triaged: each either gets a new test that kills it, or a documented reason it's acceptable (e.g. an unreachable defensive branch)
- [ ] The job's pass/fail threshold (e.g. "no new surviving mutants vs. a baseline") is explicit, not just informational output

**Guidance.**
- .gitignore's existing mutants.out*/ entry
- .github/workflows/ci.yml's fuzz job (schedule-gated, nightly) is the pattern to mirror for runtime budget

### ci: add code coverage reporting

`repo:sorocharge-core` `area:ci-release`

**Description.** No coverage tool (cargo-llvm-cov, tarpaulin) runs anywhere, and there's no coverage badge or report — despite 95+ unit tests, 35 doctests, 3 fuzz targets, and 3 proptest suites now existing, there's no single number or report tying it together.

**Why.** With this much test infrastructure already built, a coverage report is what makes gaps visible at a glance instead of only being found by someone manually reading every file (the way the delegated-threshold gap and the MAX_LEN boundary gaps in this same backlog were found).

**Acceptance criteria.**
- [ ] cargo-llvm-cov (or equivalent) runs in CI and produces a report
- [ ] A badge in README.md reflects the real, current number
- [ ] The report is uploaded somewhere reviewable (Codecov, or a committed HTML artifact) rather than only printed to the CI log

**Guidance.**
- .github/workflows/ci.yml for where to add the job
- README.md's existing badge section for where to add the coverage badge

### refactor: deduplicate retry_get between sorocharge-x402::client and sorocharge-mpp::client

`repo:sorocharge-core` `area:ci-release`

**Description.** Both crates' client.rs define an almost byte-identical retry_get function (bounded retry with backoff for transient HTTP failures), differing only in which crate's Error type they construct.

**Why.** Same drift risk this project has already fixed twice (network_id_hash, caip2_for_passphrase): two copies of the same retry/backoff logic can silently diverge the next time one is tuned and the other isn't.

**Acceptance criteria.**
- [ ] The retry/backoff logic lives in one place (e.g. sorocharge-signer, or a small shared internal crate) with each client's thin wrapper only translating the error type
- [ ] No behavior change to either crate's public API or retry semantics
- [ ] Existing tests for both clients' retry behavior still pass unmodified

**Guidance.**
- crates/sorocharge-x402/src/client.rs and crates/sorocharge-mpp/src/client.rs's retry_get functions
- sorocharge-signer::network already holds the precedent for this kind of shared-utility extraction

### docs: update THREAT_MODEL.md for the malware-scan CI gate

`repo:sorocharge-core` `area:ci-release`

**Description.** THREAT_MODEL.md doesn't mention the malware/supply-chain scan, PolinRider, or the branch-protection gate requiring it — all added after THREAT_MODEL.md was written.

**Why.** A threat model that doesn't name its own newest defense is incomplete exactly where a reviewer would look first to understand what's covered.

**Acceptance criteria.**
- [ ] THREAT_MODEL.md gets a section on the supply-chain/malicious-contributor threat class, naming the malware-scan CI gate, security/malware_iocs.json, and the branch-protection requirement
- [ ] States plainly what the scan does and doesn't catch (e.g. it scans the tracked tree, not runtime behavior)
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- THREAT_MODEL.md's existing structure/style to match
- security/malware_iocs.json, scripts/malware_scan.py, and the malware-scan job in .github/workflows/ci.yml

### docs: add a CHANGELOG.md

`repo:sorocharge-core` `area:ci-release`

**Description.** No CHANGELOG.md exists despite multiple tagged releases (v0.1.0, v0.1.1, v0.1.2) each with real behavioral changes, and dozens of merged PRs since.

**Why.** sorocharge-php already has one; sorocharge-core, the crate everything else depends on, doesn't.

**Acceptance criteria.**
- [ ] CHANGELOG.md following Keep a Changelog style, with entries for each tagged release
- [ ] An Unreleased section covering what's merged since v0.1.2
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- sorocharge-php's CHANGELOG.md as the sibling-repo style reference
- git tag -l and git log for the real release history

### chore: add a dependabot.yml

`repo:sorocharge-core` `area:ci-release`

**Description.** No .github/dependabot.yml exists for either cargo or npm (tests/golden_vectors' package.json) — every dependency bump (like this wave's own tokio advisory fix) has so far been found by someone running cargo-deny locally and noticing, not by an automated update proposal.

**Why.** .github/ directory's existing contents; sorocharge-php already has this file.

**Acceptance criteria.**
- [ ] .github/dependabot.yml covers both the cargo ecosystem (root + crates/*) and npm (tests/golden_vectors)
- [ ] A test PR (or the next real Dependabot PR) confirms it actually opens update PRs
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- sorocharge-php's .github/dependabot.yml as the sibling-repo reference
- Run the existing CI checks locally before pushing — see .github/workflows/ci.yml in sorocharge-core

### docs: add a security/README.md documenting how to add a new campaign's IOCs

`repo:sorocharge-core` `area:ci-release`

**Description.** security/malware_iocs.json's own _comment says 'each addition should cite a source (see the PR that added it)' but there's no consolidated doc for a future contributor on the actual process: where to research a new campaign, what fields are required, how the protected-files guard and scan_allowlist.json interact.

**Why.** The next PolinRider-style campaign (or its successor) will need someone unfamiliar with this scanner to add IOCs correctly and quickly — right now that knowledge only exists in this PR's own history.

**Acceptance criteria.**
- [ ] security/README.md documents the JSON schema, the sourcing-citation expectation, and the relationship between malware_iocs.json (patterns) and scan_allowlist.json (exceptions)
- [ ] Explicitly states that any change to either file requires the protected-files-guard review path, not just a passing scan
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- security/malware_iocs.json and scripts/malware_scan.py's own docstring
- Run the existing CI checks locally before pushing — see .github/workflows/ci.yml in sorocharge-core

### docs(signer): audit verify_transfer_effects's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read verify_transfer_effects in crates/sorocharge-signer/src/effects.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/effects.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit parse_address's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read parse_address in crates/sorocharge-signer/src/entry.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/entry.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit UnsignedEntry::as_xdr's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read UnsignedEntry::as_xdr in crates/sorocharge-signer/src/entry.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/entry.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit build_charge_entry's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read build_charge_entry in crates/sorocharge-signer/src/entry.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/entry.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit caip2_for_passphrase's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read caip2_for_passphrase in crates/sorocharge-signer/src/network.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/network.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit verify_entry's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read verify_entry in crates/sorocharge-signer/src/verify.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/verify.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit SignedEntry::as_xdr's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read SignedEntry::as_xdr in crates/sorocharge-signer/src/sign.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/sign.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit SignedEntry::from_xdr's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read SignedEntry::from_xdr in crates/sorocharge-signer/src/sign.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/sign.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit network_id_hash's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read network_id_hash in crates/sorocharge-signer/src/sign.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/sign.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit sign_entry's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read sign_entry in crates/sorocharge-signer/src/sign.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/sign.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(x402): audit X402Client::new's doc comment against its actual behavior

`repo:sorocharge-core` `area:x402`

**Description.** Re-read X402Client::new in crates/sorocharge-x402/src/client.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-x402/src/client.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(x402): audit X402Client::get_with_payment's doc comment against its actual behavior

`repo:sorocharge-core` `area:x402`

**Description.** Re-read X402Client::get_with_payment in crates/sorocharge-x402/src/client.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-x402/src/client.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(x402): audit Facilitator::new's doc comment against its actual behavior

`repo:sorocharge-core` `area:x402`

**Description.** Re-read Facilitator::new in crates/sorocharge-x402/src/facilitator.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-x402/src/facilitator.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(x402): audit Facilitator::verify's doc comment against its actual behavior

`repo:sorocharge-core` `area:x402`

**Description.** Re-read Facilitator::verify in crates/sorocharge-x402/src/facilitator.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-x402/src/facilitator.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(x402): audit Facilitator::settle's doc comment against its actual behavior

`repo:sorocharge-core` `area:x402`

**Description.** Re-read Facilitator::settle in crates/sorocharge-x402/src/facilitator.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-x402/src/facilitator.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(x402): audit Facilitator::supported's doc comment against its actual behavior

`repo:sorocharge-core` `area:x402`

**Description.** Re-read Facilitator::supported in crates/sorocharge-x402/src/facilitator.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-x402/src/facilitator.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(x402): audit caip2_for_passphrase's doc comment against its actual behavior

`repo:sorocharge-core` `area:x402`

**Description.** Re-read caip2_for_passphrase in crates/sorocharge-x402/src/network.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-x402/src/network.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(x402): audit parse_payment_transaction's doc comment against its actual behavior

`repo:sorocharge-core` `area:x402`

**Description.** Re-read parse_payment_transaction in crates/sorocharge-x402/src/tx.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-x402/src/tx.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(mpp): audit MppClient::new's doc comment against its actual behavior

`repo:sorocharge-core` `area:mpp`

**Description.** Re-read MppClient::new in crates/sorocharge-mpp/src/client.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-mpp/src/client.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(mpp): audit MppClient::get_with_payment's doc comment against its actual behavior

`repo:sorocharge-core` `area:mpp`

**Description.** Re-read MppClient::get_with_payment in crates/sorocharge-mpp/src/client.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-mpp/src/client.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(mpp): audit MppServer::new's doc comment against its actual behavior

`repo:sorocharge-core` `area:mpp`

**Description.** Re-read MppServer::new in crates/sorocharge-mpp/src/server.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-mpp/src/server.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(mpp): audit MppServer::build_challenge_header's doc comment against its actual behavior

`repo:sorocharge-core` `area:mpp`

**Description.** Re-read MppServer::build_challenge_header in crates/sorocharge-mpp/src/server.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-mpp/src/server.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(mpp): audit MppServer::settle_credential's doc comment against its actual behavior

`repo:sorocharge-core` `area:mpp`

**Description.** Re-read MppServer::settle_credential in crates/sorocharge-mpp/src/server.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-mpp/src/server.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(mpp): audit parse_payment_transaction's doc comment against its actual behavior

`repo:sorocharge-core` `area:mpp`

**Description.** Re-read parse_payment_transaction in crates/sorocharge-mpp/src/tx.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-mpp/src/tx.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(mpp): audit caip2_for_passphrase's doc comment against its actual behavior

`repo:sorocharge-core` `area:mpp`

**Description.** Re-read caip2_for_passphrase in crates/sorocharge-mpp/src/network.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-mpp/src/network.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### docs(signer): audit verify_delegated_threshold's doc comment against its actual behavior

`repo:sorocharge-core` `area:signer`

**Description.** Re-read verify_delegated_threshold in crates/sorocharge-signer/src/verify.rs line by line against its own doc comment. For every claim the doc comment makes (an error it returns, a check it performs, something it explicitly does or doesn't do), confirm the code actually does that — not just that the doc comment reads well.

**Why.** verify_delegated_threshold's doc comment promised an expiry check ("checked before any signature work") that never ran — both `expected` and `current_ledger` were unused parameters. That bug shipped, reviewed, and merged without anyone catching the doc/code mismatch; this audit exists because that gap is real and this is the only way to know it isn't repeated elsewhere.

**Acceptance criteria.**
- [ ] Every claim in the function's doc comment is checked against the actual implementation line by line
- [ ] Any mismatch found is fixed (either the code or the doc comment, whichever is wrong) in the same PR, with a regression test if the code was wrong
- [ ] If no mismatch is found, the PR states that explicitly — a clean audit is a valid, complete outcome

**Guidance.**
- crates/sorocharge-signer/src/verify.rs — read the whole function, not just its signature
- crates/sorocharge-signer/src/verify.rs's verify_delegated_threshold fix (same session, same class of bug) is the concrete precedent for what to look for

### feat: expose verify_delegated_threshold via the PHP binding

`repo:sorocharge-php` `area:signer`

**Description.** sorocharge-core added verify_delegated_threshold (verifies a Delegated entry's signatures against the account's real multisig/threshold policy) since this binding was built. php/src/Sorocharge.php wraps buildChargeEntry/signEntry/verifyEntry/verifyTransferEffects, but not this.

**Why.** This repo's own stated pattern is to wrap sorocharge-signer's public functions one for one; this one function is now missing from that mapping, and PHP callers using Delegated credentials have no way to reach it.

**Acceptance criteria.**
- [ ] A new static method (e.g. Sorocharge::verifyDelegatedThreshold) wraps the Rust function with the same PHP-native-types-at-the-boundary discipline as the existing methods
- [ ] A new PHPUnit test exercises both the accept and reject paths
- [ ] The stub file is updated to match

**Guidance.**
- php/src/Sorocharge.php's existing verifyEntry wrapper as the pattern to follow
- sorocharge-core's crates/sorocharge-signer/src/verify.rs for the current function signature — it was fixed for a real expiry-check bug this same session, confirm you're wrapping the fixed version

### docs: add a THREAT_MODEL.md

`repo:sorocharge-php` `area:ci-release`

**Description.** sorocharge-core has one (added since this binding's own docs were last reviewed); sorocharge-php, which crosses an FFI boundary and has its own distinct failure modes (panics across FFI, PHP-side memory limits, extension-loading conflicts), doesn't.

**Why.** An FFI boundary is exactly where a 'this can't happen in safe Rust' assumption is most likely to be wrong — this repo's own CLAUDE.md already discusses panic-catching and memory-limit behavior piecemeal; nothing consolidates it as a threat model.

**Acceptance criteria.**
- [ ] THREAT_MODEL.md names the FFI-specific threat classes: panics crossing the boundary, PHP memory-limit exhaustion during signing (already tested in tests/integration/SignEntryTest.php), and the supply-chain/malicious-contributor class the malware-scan job defends against
- [ ] Links to sorocharge-core's THREAT_MODEL.md for the shared signing-engine threats rather than duplicating them
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- sorocharge-core's THREAT_MODEL.md as the sibling-repo reference for structure
- tests/integration/SignEntryTest.php's memory-limit test is a concrete example of a threat already defended against but not documented as such

### test: scripts/malware_scan.py has zero automated test coverage

`repo:sorocharge-php` `area:ci-release`

**Description.** Same gap as sorocharge-core#(this wave's equivalent): the scanner required by branch protection on every PR was verified ad hoc, never committed as a repeatable test, in this repo's own copy of the script.

**Why.** Each repo's copy of the scanner is independently maintainable (and has already diverged slightly — different ENCODED_BLOB_EXCLUDED paths, a different scan_allowlist.json entry for this repo's proc_open test) — a regression here needs its own test, not just a cross-reference to core's.

**Acceptance criteria.**
- [ ] A test harness exercises every check category against this repo's own copy of the scanner
- [ ] A test confirms this repo's specific scan_allowlist.json entry (tests/integration/SignEntryTest.php's proc_open) is correctly exempted
- [ ] A test confirms the protected-files guard fires on this repo's own security/ files

**Guidance.**
- scripts/malware_scan.py and security/scan_allowlist.json in this repo
- Run the existing CI checks locally before pushing — see .github/workflows/ci.yml in sorocharge-php

### chore: add Rust-level unit tests for the FFI conversion layer

`repo:sorocharge-php` `area:signer`

**Description.** src/charge_params.rs, src/errors.rs, src/signer.rs, src/verifier.rs are the Rust side of the FFI boundary (converting between PHP-native values and sorocharge-signer's types), tested today only indirectly through PHPUnit calling into the compiled extension. There's no #[cfg(test)] module in any of these files exercising the conversion logic on its own, in pure Rust.

**Why.** A conversion bug (e.g. a sign/truncation error turning a PHP string amount into the wrong i128) could be masked by PHPUnit if the specific test case it happens to run doesn't hit that value, where a direct Rust unit test of the conversion function would catch it immediately and faster.

**Acceptance criteria.**
- [ ] At least src/charge_params.rs and src/errors.rs gain #[cfg(test)] unit tests exercising their conversion functions directly (no PHP runtime needed)
- [ ] cargo test (not composer test) runs and passes these
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- src/charge_params.rs, src/errors.rs for the conversion functions to target
- This is explicitly about adding a faster, PHP-independent layer under the existing PHPUnit coverage, not replacing it

### perf: benchmark the FFI call overhead itself

`repo:sorocharge-php` `area:ci-release`

**Description.** No benchmark exists for the actual cost of crossing the FFI boundary (PHP calling into the compiled Rust extension) separate from the signing/verification work itself — unlike sorocharge-core, which now has criterion benchmarks for its pure-Rust hot path.

**Why.** A native extension's whole value proposition is being faster than a pure-PHP implementation; without a number for the FFI overhead itself, there's no way to tell how much of any future regression is the Rust-side logic versus the boundary crossing.

**Acceptance criteria.**
- [ ] A benchmark (PHPBench, or a simple timed loop in an example script) measures Sorocharge::verifyEntry's wall-clock cost against a fixed fixture, separated conceptually from sorocharge-core's own already-benchmarked verify_entry cost
- [ ] A baseline number is recorded in the PR description
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- sorocharge-core's benches/signer_benchmarks.rs is the sibling-repo reference for what's already measured on the Rust side
- Run the existing CI checks locally before pushing — see .github/workflows/ci.yml in sorocharge-php

### docs: add a security/README.md documenting how to add a new campaign's IOCs

`repo:sorocharge-php` `area:ci-release`

**Description.** Same gap as sorocharge-core's equivalent — security/malware_iocs.json's own _comment points to 'the PR that added it' for sourcing, but there's no consolidated process doc in this repo's own security/ directory.

**Why.** This repo's copy of the scanner can diverge from core's (it already has one extra allowlist entry); a contributor adding a new campaign here needs the same guidance independently.

**Acceptance criteria.**
- [ ] security/README.md documents the JSON schema and sourcing-citation expectation for this repo specifically
- [ ] States the protected-files-guard review requirement
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- security/malware_iocs.json and scripts/malware_scan.py's docstring in this repo
- Run the existing CI checks locally before pushing — see .github/workflows/ci.yml in sorocharge-php

### test: confirm AmountMismatchException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/AmountMismatchException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on AmountMismatchException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/AmountMismatchException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm AssetMismatchException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/AssetMismatchException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on AssetMismatchException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/AssetMismatchException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm DuplicateDelegateSignerException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/DuplicateDelegateSignerException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on DuplicateDelegateSignerException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/DuplicateDelegateSignerException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm EmptyDelegateSignersException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/EmptyDelegateSignersException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on EmptyDelegateSignersException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/EmptyDelegateSignersException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm ExpectedTransferMissingException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/ExpectedTransferMissingException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on ExpectedTransferMissingException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/ExpectedTransferMissingException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm ExpirationExceedsAllowanceException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/ExpirationExceedsAllowanceException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on ExpirationExceedsAllowanceException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/ExpirationExceedsAllowanceException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm ExpiredEntryException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/ExpiredEntryException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on ExpiredEntryException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/ExpiredEntryException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm InternalErrorException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/InternalErrorException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on InternalErrorException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/InternalErrorException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm InvalidAddressException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/InvalidAddressException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on InvalidAddressException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/InvalidAddressException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm InvalidSignatureException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/InvalidSignatureException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on InvalidSignatureException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/InvalidSignatureException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm NoMatchingCredentialNodeException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/NoMatchingCredentialNodeException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on NoMatchingCredentialNodeException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/NoMatchingCredentialNodeException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm PayerMismatchException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/PayerMismatchException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on PayerMismatchException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/PayerMismatchException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm RecipientMismatchException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/RecipientMismatchException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on RecipientMismatchException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/RecipientMismatchException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm SigningFailedException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/SigningFailedException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on SigningFailedException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/SigningFailedException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm SimulationEventsMalformedException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/SimulationEventsMalformedException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on SimulationEventsMalformedException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/SimulationEventsMalformedException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm UnexpectedBalanceChangeException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/UnexpectedBalanceChangeException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on UnexpectedBalanceChangeException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/UnexpectedBalanceChangeException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm UnexpectedInvocationShapeException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/UnexpectedInvocationShapeException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on UnexpectedInvocationShapeException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/UnexpectedInvocationShapeException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm UnsupportedCredentialTypeException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/UnsupportedCredentialTypeException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on UnsupportedCredentialTypeException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/UnsupportedCredentialTypeException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm XdrEncodingFailedException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/XdrEncodingFailedException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on XdrEncodingFailedException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/XdrEncodingFailedException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### test: confirm SorochargeException exactly maps its corresponding Rust SorochargeError variant

`repo:sorocharge-php` `area:signer`

**Description.** Audit php/src/SorochargeException.php against the Rust SorochargeError variant it maps (in sorocharge-core's crates/sorocharge-signer/src/error.rs) field by field: every field the Rust variant carries is present and correctly typed on the PHP side, the exception message is actionable, and there's a PHPUnit test that actually triggers this specific exception (not just constructs it by hand).

**Why.** This project's cross-FFI error-mapping rule (CLAUDE.md: 'Every SorochargeError variant in the Rust core maps to a specific SorochargeException subclass... so a PHP caller can catch specifically') is only as good as each mapping being individually verified — a field silently dropped or mistyped at this boundary fails exactly the specific-catch guarantee the whole design exists for.

**Acceptance criteria.**
- [ ] Every field the Rust error variant carries exists on SorochargeException with the correct PHP-native type (strings for amounts/u32s per this repo's own no-native-i128 rule, not PHP int)
- [ ] A PHPUnit test exercises the real extension (not a hand-constructed exception) and confirms this exact class is thrown, not a parent class or a generic SorochargeException
- [ ] If a mismatch is found, it's fixed in the same PR with the test that would have caught it

**Guidance.**
- php/src/SorochargeException.php and the corresponding variant in sorocharge-core's error.rs
- tests/integration/ExceptionHierarchyTest.php for the existing pattern, if this class is already covered there — extend it rather than duplicating

### docs(signer): audit SorochargeError::InvalidAddress's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** InvalidAddress's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::InvalidAddress is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::InvalidAddress' across the crate for every return site

### docs(signer): audit SorochargeError::UnsupportedCredentialType's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** UnsupportedCredentialType's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::UnsupportedCredentialType is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::UnsupportedCredentialType' across the crate for every return site

### docs(signer): audit SorochargeError::EmptyDelegateSigners's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** EmptyDelegateSigners's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::EmptyDelegateSigners is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::EmptyDelegateSigners' across the crate for every return site

### docs(signer): audit SorochargeError::DuplicateDelegateSigner's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** DuplicateDelegateSigner's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::DuplicateDelegateSigner is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::DuplicateDelegateSigner' across the crate for every return site

### docs(signer): audit SorochargeError::ExpiredEntry's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** ExpiredEntry's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::ExpiredEntry is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::ExpiredEntry' across the crate for every return site

### docs(signer): audit SorochargeError::ExpirationExceedsAllowance's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** ExpirationExceedsAllowance's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::ExpirationExceedsAllowance is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::ExpirationExceedsAllowance' across the crate for every return site

### docs(signer): audit SorochargeError::UnexpectedInvocationShape's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** UnexpectedInvocationShape's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::UnexpectedInvocationShape is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::UnexpectedInvocationShape' across the crate for every return site

### docs(signer): audit SorochargeError::AssetMismatch's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** AssetMismatch's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::AssetMismatch is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::AssetMismatch' across the crate for every return site

### docs(signer): audit SorochargeError::PayerMismatch's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** PayerMismatch's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::PayerMismatch is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::PayerMismatch' across the crate for every return site

### docs(signer): audit SorochargeError::AmountMismatch's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** AmountMismatch's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::AmountMismatch is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::AmountMismatch' across the crate for every return site

### docs(signer): audit SorochargeError::AmountNonPositive's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** AmountNonPositive's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::AmountNonPositive is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::AmountNonPositive' across the crate for every return site

### docs(signer): audit SorochargeError::RecipientMismatch's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** RecipientMismatch's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::RecipientMismatch is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::RecipientMismatch' across the crate for every return site

### docs(signer): audit SorochargeError::InvalidSignature's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** InvalidSignature's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::InvalidSignature is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::InvalidSignature' across the crate for every return site

### docs(signer): audit SorochargeError::NoMatchingCredentialNode's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** NoMatchingCredentialNode's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::NoMatchingCredentialNode is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::NoMatchingCredentialNode' across the crate for every return site

### docs(signer): audit SorochargeError::UnsupportedNetwork's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** UnsupportedNetwork's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::UnsupportedNetwork is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::UnsupportedNetwork' across the crate for every return site

### docs(signer): audit SorochargeError::SimulationEventsMalformed's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** SimulationEventsMalformed's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::SimulationEventsMalformed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::SimulationEventsMalformed' across the crate for every return site

### docs(signer): audit SorochargeError::UnexpectedBalanceChange's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** UnexpectedBalanceChange's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::UnexpectedBalanceChange is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::UnexpectedBalanceChange' across the crate for every return site

### docs(signer): audit SorochargeError::ExpectedTransferMissing's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** ExpectedTransferMissing's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::ExpectedTransferMissing is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::ExpectedTransferMissing' across the crate for every return site

### docs(signer): audit SorochargeError::SigningFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** SigningFailed's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::SigningFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::SigningFailed' across the crate for every return site

### docs(signer): audit SorochargeError::XdrEncodingFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:signer`

**Description.** XdrEncodingFailed's own doc comment on the SorochargeError enum in crates/sorocharge-signer/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning SorochargeError::XdrEncodingFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-signer/src/error.rs for the variant's own doc comment
- grep -rn 'SorochargeError::XdrEncodingFailed' across the crate for every return site

### docs(x402): audit X402Error::HttpRequestFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** HttpRequestFailed's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::HttpRequestFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::HttpRequestFailed' across the crate for every return site

### docs(x402): audit X402Error::UnexpectedStatus's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** UnexpectedStatus's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::UnexpectedStatus is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::UnexpectedStatus' across the crate for every return site

### docs(x402): audit X402Error::MissingPaymentRequiredHeader's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** MissingPaymentRequiredHeader's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::MissingPaymentRequiredHeader is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::MissingPaymentRequiredHeader' across the crate for every return site

### docs(x402): audit X402Error::InvalidPaymentRequired's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** InvalidPaymentRequired's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::InvalidPaymentRequired is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::InvalidPaymentRequired' across the crate for every return site

### docs(x402): audit X402Error::NoAcceptablePaymentRequirements's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** NoAcceptablePaymentRequirements's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::NoAcceptablePaymentRequirements is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::NoAcceptablePaymentRequirements' across the crate for every return site

### docs(x402): audit X402Error::UnsupportedNetwork's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** UnsupportedNetwork's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::UnsupportedNetwork is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::UnsupportedNetwork' across the crate for every return site

### docs(x402): audit X402Error::Signing's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** Signing's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::Signing is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::Signing' across the crate for every return site

### docs(x402): audit X402Error::XdrEncodingFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** XdrEncodingFailed's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::XdrEncodingFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::XdrEncodingFailed' across the crate for every return site

### docs(x402): audit X402Error::InvalidPaymentPayload's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** InvalidPaymentPayload's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::InvalidPaymentPayload is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::InvalidPaymentPayload' across the crate for every return site

### docs(x402): audit X402Error::XdrDecodingFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** XdrDecodingFailed's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::XdrDecodingFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::XdrDecodingFailed' across the crate for every return site

### docs(x402): audit X402Error::UnexpectedTransactionShape's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** UnexpectedTransactionShape's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::UnexpectedTransactionShape is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::UnexpectedTransactionShape' across the crate for every return site

### docs(x402): audit X402Error::ForbiddenCredentialType's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** ForbiddenCredentialType's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::ForbiddenCredentialType is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::ForbiddenCredentialType' across the crate for every return site

### docs(x402): audit X402Error::FacilitatorAddressConflict's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** FacilitatorAddressConflict's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::FacilitatorAddressConflict is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::FacilitatorAddressConflict' across the crate for every return site

### docs(x402): audit X402Error::RpcFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** RpcFailed's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::RpcFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::RpcFailed' across the crate for every return site

### docs(x402): audit X402Error::FeeExceedsCeiling's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** FeeExceedsCeiling's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::FeeExceedsCeiling is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::FeeExceedsCeiling' across the crate for every return site

### docs(x402): audit X402Error::SettlementFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:x402`

**Description.** SettlementFailed's own doc comment on the X402Error enum in crates/sorocharge-x402/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning X402Error::SettlementFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-x402/src/error.rs for the variant's own doc comment
- grep -rn 'X402Error::SettlementFailed' across the crate for every return site

### docs(mpp): audit MppError::HttpRequestFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** HttpRequestFailed's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::HttpRequestFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::HttpRequestFailed' across the crate for every return site

### docs(mpp): audit MppError::UnexpectedStatus's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** UnexpectedStatus's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::UnexpectedStatus is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::UnexpectedStatus' across the crate for every return site

### docs(mpp): audit MppError::MissingChallenge's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** MissingChallenge's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::MissingChallenge is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::MissingChallenge' across the crate for every return site

### docs(mpp): audit MppError::InvalidChallenge's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** InvalidChallenge's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::InvalidChallenge is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::InvalidChallenge' across the crate for every return site

### docs(mpp): audit MppError::UnsupportedMethod's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** UnsupportedMethod's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::UnsupportedMethod is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::UnsupportedMethod' across the crate for every return site

### docs(mpp): audit MppError::UnsupportedIntent's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** UnsupportedIntent's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::UnsupportedIntent is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::UnsupportedIntent' across the crate for every return site

### docs(mpp): audit MppError::InvalidChargeRequest's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** InvalidChargeRequest's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::InvalidChargeRequest is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::InvalidChargeRequest' across the crate for every return site

### docs(mpp): audit MppError::UnsupportedNetwork's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** UnsupportedNetwork's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::UnsupportedNetwork is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::UnsupportedNetwork' across the crate for every return site

### docs(mpp): audit MppError::ChallengeExpired's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** ChallengeExpired's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::ChallengeExpired is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::ChallengeExpired' across the crate for every return site

### docs(mpp): audit MppError::Signing's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** Signing's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::Signing is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::Signing' across the crate for every return site

### docs(mpp): audit MppError::XdrEncodingFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp`

**Description.** XdrEncodingFailed's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::XdrEncodingFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::XdrEncodingFailed' across the crate for every return site

## Low — 100 points (30)

### test(x402): add boundary tests for MAX_AMOUNT_LEN

`repo:sorocharge-core` `area:x402` `good first issue`

**Description.** MAX_AMOUNT_LEN in crates/sorocharge-x402/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_AMOUNT_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_AMOUNT_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_AMOUNT_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-x402/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-x402/src/types.rs`

### test(x402): add boundary tests for MAX_DESCRIPTION_LEN

`repo:sorocharge-core` `area:x402` `good first issue`

**Description.** MAX_DESCRIPTION_LEN in crates/sorocharge-x402/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_DESCRIPTION_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_DESCRIPTION_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_DESCRIPTION_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-x402/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-x402/src/types.rs`

### test(x402): add boundary tests for MAX_ERROR_MESSAGE_LEN

`repo:sorocharge-core` `area:x402` `good first issue`

**Description.** MAX_ERROR_MESSAGE_LEN in crates/sorocharge-x402/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_ERROR_MESSAGE_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_ERROR_MESSAGE_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_ERROR_MESSAGE_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-x402/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-x402/src/types.rs`

### test(x402): add boundary tests for MAX_MIME_TYPE_LEN

`repo:sorocharge-core` `area:x402` `good first issue`

**Description.** MAX_MIME_TYPE_LEN in crates/sorocharge-x402/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_MIME_TYPE_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_MIME_TYPE_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_MIME_TYPE_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-x402/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-x402/src/types.rs`

### test(x402): add boundary tests for MAX_NETWORK_LEN

`repo:sorocharge-core` `area:x402` `good first issue`

**Description.** MAX_NETWORK_LEN in crates/sorocharge-x402/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_NETWORK_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_NETWORK_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_NETWORK_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-x402/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-x402/src/types.rs`

### test(x402): add boundary tests for MAX_SCHEME_LEN

`repo:sorocharge-core` `area:x402` `good first issue`

**Description.** MAX_SCHEME_LEN in crates/sorocharge-x402/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_SCHEME_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_SCHEME_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_SCHEME_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-x402/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-x402/src/types.rs`

### test(x402): add boundary tests for MAX_STRKEY_LEN

`repo:sorocharge-core` `area:x402` `good first issue`

**Description.** MAX_STRKEY_LEN in crates/sorocharge-x402/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_STRKEY_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_STRKEY_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_STRKEY_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-x402/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-x402/src/types.rs`

### test(x402): add boundary tests for MAX_URL_LEN

`repo:sorocharge-core` `area:x402` `good first issue`

**Description.** MAX_URL_LEN in crates/sorocharge-x402/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_URL_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_URL_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_URL_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-x402/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-x402/src/types.rs`

### test(mpp): add boundary tests for MAX_DESCRIPTION_LEN

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** MAX_DESCRIPTION_LEN in crates/sorocharge-mpp/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_DESCRIPTION_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_DESCRIPTION_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_DESCRIPTION_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-mpp/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-mpp/src/types.rs`

### test(mpp): add boundary tests for MAX_REALM_LEN

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** MAX_REALM_LEN in crates/sorocharge-mpp/src/types.rs is deserialized against and enforced, but no test exercises its exact boundary — a value exactly at the limit (should pass) and one byte over (should be rejected with a specific error, not silently truncated or panicking).

**Why.** MAX_REALM_LEN exists specifically because of the field-length-cap work this project already did (per-field bounds against a malicious/compromised resource server) — an off-by-one in the comparison would quietly defeat the exact protection that work was for.

**Acceptance criteria.**
- [ ] A test with a value exactly MAX_REALM_LEN bytes long deserializes successfully
- [ ] A test with a value one byte over MAX_REALM_LEN is rejected with a specific error naming the field
- [ ] Both tests use the real deserializer path (serde), not a hand-called bounds-check function

**Guidance.**
- crates/sorocharge-mpp/src/types.rs
- Find where this constant is actually enforced (the bounded_string/bounded_opt_string deserializer helpers) before writing the test

**Entry point.** `crates/sorocharge-mpp/src/types.rs`

### docs: add a runnable doctest example to caip2_for_passphrase

`repo:sorocharge-core` `area:signer` `good first issue`

**Description.** caip2_for_passphrase in crates/sorocharge-signer/src/network.rs was added/re-exported since the last doctest pass and has no `# Examples` section — `cargo test --doc` doesn't exercise it at all.

**Why.** The rest of sorocharge-signer's public API has runnable examples; caip2_for_passphrase is a gap left by landing after that pass, not a deliberate omission.

**Acceptance criteria.**
- [ ] caip2_for_passphrase's doc comment gains a ```rust fenced example that compiles and runs under `cargo test --doc`
- [ ] The example uses realistic values consistent with the rest of the crate's fixtures
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- crates/sorocharge-signer/src/network.rs
- crates/sorocharge-signer/src/verify.rs's verify_entry doctest is the closest existing pattern to copy from

**Entry point.** `crates/sorocharge-signer/src/network.rs`

### docs: add a runnable doctest example to network_id_hash

`repo:sorocharge-core` `area:signer` `good first issue`

**Description.** network_id_hash in crates/sorocharge-signer/src/sign.rs was added/re-exported since the last doctest pass and has no `# Examples` section — `cargo test --doc` doesn't exercise it at all.

**Why.** The rest of sorocharge-signer's public API has runnable examples; network_id_hash is a gap left by landing after that pass, not a deliberate omission.

**Acceptance criteria.**
- [ ] network_id_hash's doc comment gains a ```rust fenced example that compiles and runs under `cargo test --doc`
- [ ] The example uses realistic values consistent with the rest of the crate's fixtures
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- crates/sorocharge-signer/src/sign.rs
- crates/sorocharge-signer/src/verify.rs's verify_entry doctest is the closest existing pattern to copy from

**Entry point.** `crates/sorocharge-signer/src/sign.rs`

### docs: add a runnable doctest example to verify_delegated_threshold

`repo:sorocharge-core` `area:signer` `good first issue`

**Description.** verify_delegated_threshold in crates/sorocharge-signer/src/verify.rs was added/re-exported since the last doctest pass and has no `# Examples` section — `cargo test --doc` doesn't exercise it at all.

**Why.** The rest of sorocharge-signer's public API has runnable examples; verify_delegated_threshold is a gap left by landing after that pass, not a deliberate omission.

**Acceptance criteria.**
- [ ] verify_delegated_threshold's doc comment gains a ```rust fenced example that compiles and runs under `cargo test --doc`
- [ ] The example uses realistic values consistent with the rest of the crate's fixtures
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- crates/sorocharge-signer/src/verify.rs
- crates/sorocharge-signer/src/verify.rs's verify_entry doctest is the closest existing pattern to copy from

**Entry point.** `crates/sorocharge-signer/src/verify.rs`

### docs: add a runnable doctest example to parse_address

`repo:sorocharge-core` `area:signer` `good first issue`

**Description.** parse_address in crates/sorocharge-signer/src/entry.rs was added/re-exported since the last doctest pass and has no `# Examples` section — `cargo test --doc` doesn't exercise it at all.

**Why.** The rest of sorocharge-signer's public API has runnable examples; parse_address is a gap left by landing after that pass, not a deliberate omission.

**Acceptance criteria.**
- [ ] parse_address's doc comment gains a ```rust fenced example that compiles and runs under `cargo test --doc`
- [ ] The example uses realistic values consistent with the rest of the crate's fixtures
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- crates/sorocharge-signer/src/entry.rs
- crates/sorocharge-signer/src/verify.rs's verify_entry doctest is the closest existing pattern to copy from

**Entry point.** `crates/sorocharge-signer/src/entry.rs`

### docs: add a runnable example to Sorocharge::buildChargeEntry's docblock

`repo:sorocharge-php` `area:signer` `good first issue`

**Description.** Sorocharge::buildChargeEntry in php/src/Sorocharge.php has a docblock describing parameters and return type, but no worked example showing realistic input/output values a PHP integrator could copy from directly.

**Why.** examples/laravel-middleware.php and examples/plain-composer-app.php show the whole flow end to end, but a reader of buildChargeEntry's own docblock in an IDE has no inline example without jumping to a separate file.

**Acceptance criteria.**
- [ ] buildChargeEntry's docblock gains a concrete example with realistic-looking values (matching the style of this repo's own test fixtures)
- [ ] The example is consistent with (not a copy-paste divergence from) examples/plain-composer-app.php's actual usage
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- php/src/Sorocharge.php
- examples/plain-composer-app.php for realistic values to reuse

**Entry point.** `php/src/Sorocharge.php`

### docs: add a runnable example to Sorocharge::signEntry's docblock

`repo:sorocharge-php` `area:signer` `good first issue`

**Description.** Sorocharge::signEntry in php/src/Sorocharge.php has a docblock describing parameters and return type, but no worked example showing realistic input/output values a PHP integrator could copy from directly.

**Why.** examples/laravel-middleware.php and examples/plain-composer-app.php show the whole flow end to end, but a reader of signEntry's own docblock in an IDE has no inline example without jumping to a separate file.

**Acceptance criteria.**
- [ ] signEntry's docblock gains a concrete example with realistic-looking values (matching the style of this repo's own test fixtures)
- [ ] The example is consistent with (not a copy-paste divergence from) examples/plain-composer-app.php's actual usage
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- php/src/Sorocharge.php
- examples/plain-composer-app.php for realistic values to reuse

**Entry point.** `php/src/Sorocharge.php`

### docs: add a runnable example to Sorocharge::verifyEntry's docblock

`repo:sorocharge-php` `area:signer` `good first issue`

**Description.** Sorocharge::verifyEntry in php/src/Sorocharge.php has a docblock describing parameters and return type, but no worked example showing realistic input/output values a PHP integrator could copy from directly.

**Why.** examples/laravel-middleware.php and examples/plain-composer-app.php show the whole flow end to end, but a reader of verifyEntry's own docblock in an IDE has no inline example without jumping to a separate file.

**Acceptance criteria.**
- [ ] verifyEntry's docblock gains a concrete example with realistic-looking values (matching the style of this repo's own test fixtures)
- [ ] The example is consistent with (not a copy-paste divergence from) examples/plain-composer-app.php's actual usage
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- php/src/Sorocharge.php
- examples/plain-composer-app.php for realistic values to reuse

**Entry point.** `php/src/Sorocharge.php`

### docs: add a runnable example to Sorocharge::verifyTransferEffects's docblock

`repo:sorocharge-php` `area:signer` `good first issue`

**Description.** Sorocharge::verifyTransferEffects in php/src/Sorocharge.php has a docblock describing parameters and return type, but no worked example showing realistic input/output values a PHP integrator could copy from directly.

**Why.** examples/laravel-middleware.php and examples/plain-composer-app.php show the whole flow end to end, but a reader of verifyTransferEffects's own docblock in an IDE has no inline example without jumping to a separate file.

**Acceptance criteria.**
- [ ] verifyTransferEffects's docblock gains a concrete example with realistic-looking values (matching the style of this repo's own test fixtures)
- [ ] The example is consistent with (not a copy-paste divergence from) examples/plain-composer-app.php's actual usage
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- php/src/Sorocharge.php
- examples/plain-composer-app.php for realistic values to reuse

**Entry point.** `php/src/Sorocharge.php`

### docs(mpp): audit MppError::XdrDecodingFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** XdrDecodingFailed's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::XdrDecodingFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::XdrDecodingFailed' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::InvalidCredential's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** InvalidCredential's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::InvalidCredential is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::InvalidCredential' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::UnexpectedTransactionShape's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** UnexpectedTransactionShape's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::UnexpectedTransactionShape is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::UnexpectedTransactionShape' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::ForbiddenCredentialType's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** ForbiddenCredentialType's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::ForbiddenCredentialType is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::ForbiddenCredentialType' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::PushModeForbidsFeePayer's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** PushModeForbidsFeePayer's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::PushModeForbidsFeePayer is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::PushModeForbidsFeePayer' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::ServerAddressConflict's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** ServerAddressConflict's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::ServerAddressConflict is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::ServerAddressConflict' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::RpcFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** RpcFailed's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::RpcFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::RpcFailed' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::HashAlreadyConsumed's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** HashAlreadyConsumed's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::HashAlreadyConsumed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::HashAlreadyConsumed' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::VerificationFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** VerificationFailed's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::VerificationFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::VerificationFailed' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### docs(mpp): audit MppError::SettlementFailed's doc comment against every place it's returned

`repo:sorocharge-core` `area:mpp` `good first issue`

**Description.** SettlementFailed's own doc comment on the MppError enum in crates/sorocharge-mpp/src/error.rs describes one specific condition. Find every call site across the crate that returns this variant and confirm each one genuinely matches that documented condition — not a related-but-distinct condition folded in because a more specific variant wasn't added at the time.

**Why.** This is the enum-level counterpart to the per-function doc audit elsewhere in this backlog: a function's doc comment can accurately list which variants it returns while the variant's own meaning has quietly drifted from what any individual call site actually does — a different failure mode than the one verify_delegated_threshold had, equally undetectable without someone actually checking.

**Acceptance criteria.**
- [ ] Every call site returning MppError::SettlementFailed is found (grep is a start, not proof — confirm each one by reading it)
- [ ] Each is checked against the variant's own doc comment on the enum
- [ ] Any call site that doesn't genuinely match is either fixed to return a more accurate variant or has its condition documented as a deliberate, justified fold-in
- [ ] A clean audit (no mismatch found) is reported as such and counts as complete

**Guidance.**
- crates/sorocharge-mpp/src/error.rs for the variant's own doc comment
- grep -rn 'MppError::SettlementFailed' across the crate for every return site

**Entry point.** `crates/sorocharge-mpp/src/error.rs for the variant's own doc comment`

### chore: add a CODEOWNERS entry specifically for security/ and scripts/malware_scan.py

`repo:sorocharge-core` `area:ci-release` `good first issue`

**Description.** CODEOWNERS exists but doesn't single out security/malware_iocs.json, security/scan_allowlist.json, or scripts/malware_scan.py for mandatory review — exactly the files the malware-scan job's own protected-files guard already treats as needing a human, not an automated check, to clear.

**Why.** The protected-files guard forces CI to fail when these files change; CODEOWNERS is what makes sure the right human actually gets asked, not just whoever happens to be reviewing.

**Acceptance criteria.**
- [ ] CODEOWNERS adds an explicit entry for security/ and scripts/malware_scan.py naming a real reviewer
- [ ] A test PR touching one of these files confirms the right reviewer is auto-requested
- [ ] cargo fmt --all -- --check, cargo clippy --workspace --all-targets -- -D warnings, and cargo test --workspace all still pass after the change

**Guidance.**
- .github/CODEOWNERS's existing per-crate entries as the pattern to extend
- Run the existing CI checks locally before pushing — see .github/workflows/ci.yml in sorocharge-core

**Entry point.** `.github/CODEOWNERS`

### chore: confirm the LICENSE file's copyright holder/year is accurate

`repo:sorocharge-php` `area:ci-release` `good first issue`

**Description.** sorocharge-core already had this checked (and fixed if needed) in a prior wave; sorocharge-php's own LICENSE file hasn't been.

**Why.** LICENSE at the repo root.

**Acceptance criteria.**
- [ ] The LICENSE file's copyright notice is confirmed accurate (correct holder, correct year range) or corrected
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change
- [ ] cargo fmt --all -- --check, cargo clippy --all-targets --all-features -- -D warnings, and composer test all still pass after the change

**Guidance.**
- LICENSE
- sorocharge-core's equivalent, already-resolved issue as the reference for what "accurate" means here

**Entry point.** `LICENSE`
