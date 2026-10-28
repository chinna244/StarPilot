# Mazda on StarPilot Dom

The Mazda source port is implemented on the local `mazda-on-dom` branch. StarPilot remains the base, including its planners, native permission owner, Galaxy service and companion protocol. This is a source integration with local regression and microcontroller build evidence; full AGNOS and physical vehicle qualification remain outstanding.

## Source revisions

| Component | Revision |
| --- | --- |
| StarPilotHQ/StarPilot Dom | af48674faee8f2dbe1c30e207a9f0c37cc562fcf |
| chinna244/openpilot develop | 8039965a033b3de1f3cca0f7fe6cfcae90b451e9 |
| Mazda opendbc | 7b96732d9cd9e8e4df33d8db6d43b8f49c34ed58 |
| Mazda Panda reference | daa5398504c4b33d82c597b7684f5bd5ea5a3e89 |

The Mazda stack requires API adaptation rather than a direct cherry-pick: the vehicle context is local to Mazda, preserving StarPilot's normal interface and controller signatures.

## Implemented behavior

- Imported Mazda fingerprints, firmware identification, DBC signals, measured steering envelope, radar parsing, acceleration shaping, standstill logic and radar session state machine.
- Retained learning observation and dashboard stop-sign evidence. Stock-long remains available; alpha-long retains the source EPS/radar availability gates and StarPilot's non-release opt-in.
- Kept the original two-model independent lateral admission (CX-5 2022 and CX-9 2021). Alpha-long independent lateral is admitted only on the qualifying CX-5 2022. Other Mazda platform support comes from the imported vehicle source; independent lateral admission was not widened to those platforms.
- Safety words 2/3 select measured stock/alpha-long, and 10/11 additionally declare TJA. Legacy word 0 retains its original safety behavior. Reserved bit 4 is unused; invalid profiles have no permitted transmissions.
- Physical TJA is an immutable startup setting shared by the native UI and Galaxy. Forwarding modifies only the camera-bound button copy, preserving the original receive payload.
- MAIN/ON, Cancel, brake, reverse and stale-source behavior use StarPilot's native permission checks. A healthy ordinary cruise engagement transfers only its existing physical grant; alpha still requires physical SET/RES. The standard parser exports raw `LKAS_BLOCK` immediately on steer-to-zero EPS firmware to match Panda's pause. This can produce earlier temporary steering warnings than the source's delayed non-delivery warning. The source non-delivery algorithm is retained.
- Correlated radar handback delays software-initiated stops only for finalized Mazda alpha-long sessions. Other vehicle stops retain their existing behavior. Physical ignition/power loss cannot be delayed.
- Radar ownership and restoration failures are visible through the existing onroad alert/status path. Status has bounded freshness and vehicle binding, and does not grant driving authority. Alpha-long radar takeover disables factory AEB while active.

## Tests and build boundaries

The original controller and full-stack source fixtures are retained. The original standalone controller fixture covers 1,960 frames; the separate StarPilot context replay fixture covers 7,010 frames. The upstream context harness exercises the preserved source algorithm, while standard API and actual Card/Controls/native safety tests exercise StarPilot's adapter and physical grant handling. No source replay scenario was removed.

Host tests use real, separately built Params, msgq and acados libraries under Python 3.12; no device binary is replaced by a host build. The three standard debug-signed firmware targets are Panda, panda_h7 and body_h7. Firmware compilation does not establish vehicle calibration or a complete device release.

The root `prebuilt` marker was removed so upstream prebuilt artifacts cannot silently stand in for modified source. `prebuilt.json` was not falsified or regenerated. A matching AGNOS source build is required before installation; this environment has no Docker/AGNOS build setup. No branch push, phone release, vehicle change or deployment was performed.

Latest completed local verification:

- Vehicle/golden suite: 863 tests and 12 subtests passed.
- Final actual Card/Controls/public API and complete Mazda safety run: 126 tests and 42 subtests passed, with 5 abstract test-class skips.
- Broader Mazda/lifecycle/app regression run: 1,238 tests and 56 subtests passed, with 5 abstract safety-class skips and 4 pre-existing Cap'n Proto serialization warnings.
- App/startup regression run: 189 tests and 481 subtests passed.
- Shared lifecycle/runtime/corruption run: 193 tests and 67 subtests passed.
- Cross-make policy and companion run: 531 tests and 12 subtests passed; one manifest HTTP timeout passed in its isolated rerun. Companion behavior was not changed.
- All three standard firmware targets built with the real ARM compiler. Changed-file Ruff and Git whitespace checks pass.

The native golden audit compares all 7,010 frames against the previous native snapshot: only `steerFaultTemporary` changes in 404 stock-long CX-5 frames; every CAN byte and other recorded field is identical. The two original upstream fixtures remain byte-for-byte unchanged.

Exact final counts, command scopes and artifact hashes are in the delivery verification report. These runs overlap; counts are not an aggregate.

## Attribution

Mazda-specific imported files retain their original copyright notices, including Zeph Leggett's zoompilot notices. Upstream notices are preserved in [opendbc-LICENSE](opendbc-LICENSE) and [upstream-LICENSE.md](upstream-LICENSE.md).

This software is licensed under a custom license requiring permission for use.

This project uses software from Haibin Wen and SUNNYPILOT LLC and is licensed under a custom license requiring permission for use.
