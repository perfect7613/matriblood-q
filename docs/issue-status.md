# Implementation Status

## Completed in this pass

### Issue #2 - Seed the first end-to-end demo spine

- Added project monorepo layout.
- Added deterministic PPH demo scenario.
- Added Supabase schema and seed SQL.
- Added `/scenario` API endpoint.
- Added dashboard view for case, inventory, and readiness.

### Issue #3 - Parse manual emergency transcripts into reviewed cases

- Added manual transcript input in the dashboard.
- Added `/parse` API endpoint.
- Added TokenRouter client path with deterministic fallback.
- Added parser tests for noisy PPH-style requests.

### Issue #4 - Add greedy procurement baseline

- Added nearest-source greedy baseline module.
- Added baseline API comparison output.
- Added tests confirming the seeded nearest-source baseline is incomplete.

### Issue #5 - Implement Qiskit optimized procurement and baseline comparison

- Added Qiskit `QuadraticProgram` formulation metadata.
- Added deterministic exact fallback search for reliable MVP solving.
- Added `/compare` endpoint returning baseline and optimized results.
- Added dashboard comparison panel.
- Added tests confirming the optimizer completes the demo kit.

### Issue #6 - Connect Elato hardware voice transcripts into the case flow

- Added hardware setup checklist and PlatformIO configuration notes.
- Added dashboard label and fallback path for manual transcript flow.
- The actual ESP32-to-Elato-Deno transcript path still needs live hardware verification.

## Still needed for live hardware

- Clone/run the ElatoAI Deno WebSocket server.
- Apply Elato's Supabase schema if using its `messages` and `conversations` tables directly.
- Flash ESP32 with the laptop LAN IP in `firmware-arduino/src/Config.cpp`.
- Confirm a real spoken transcript lands in Supabase.
- Wire the dashboard to read the Elato transcript row automatically instead of manual paste.

