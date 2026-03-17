# V2 iOS GitHub Issue Backlog

This backlog translates `co_ins_2.md` into independently testable, modular issues grouped by milestone.

## Milestone 1: Project Setup

### Issue 1: Add V2 archive feature flag scaffold
Description:
- Add a compile-time and runtime feature flag for archive storage in iOS app config.
- This de-risks rollout and allows side-by-side behavior checks.

Acceptance Criteria:
- Flag exists in build config and runtime settings.
- Default is OFF for all production builds.
- Turning the flag ON enables archive code paths without app crash.

Tasks:
- Add `enableArchiveStorageV2` config key.
- Add centralized flag access helper.
- Gate all archive entry points behind the flag.
- Add unit tests for default and override behavior.

Dependencies:
- None.

Labels:
- feature
- ios
- backend

### Issue 2: Define archive data model contracts
Description:
- Define Swift models for chunk metadata and serialized payload.
- Stable contracts prevent format drift across modules.

Acceptance Criteria:
- `ArchiveChunk`, `ArchiveIndexEntry`, and serialization contracts are defined.
- Contracts are versioned (v1 schema field included).
- Codable roundtrip tests pass.

Tasks:
- Create model files with Codable structs.
- Add schema version field and comments on compatibility.
- Add encode/decode unit tests for sample payloads.

Dependencies:
- Issue 1.

Labels:
- feature
- ios
- backend

## Milestone 2: Core Archive Infrastructure

### Issue 3: Create ArchiveManager skeleton in iOS storage layer
Description:
- Introduce ArchiveManager with `archiveOldMessages(threadId:)` and `loadArchivedChunk(chunkId:)`.
- Establishes stable orchestration points before behavior is implemented.

Acceptance Criteria:
- Class compiles and methods are callable.
- Methods return placeholder values and TODO errors where applicable.
- Unit test validates invocation shape.

Tasks:
- Add ArchiveManager file and protocol.
- Register manager in dependency container.
- Add skeleton tests and compile checks.

Dependencies:
- Issue 2.

Labels:
- feature
- ios
- backend

### Issue 4: Implement monthly/message-count chunk planner
Description:
- Build chunk planning logic by month with optional max-message boundary.
- Deterministic chunking is required for indexing and stable restore.

Acceptance Criteria:
- Messages are grouped by month by default.
- Optional split at ~1000 messages per chunk works.
- Chunk boundaries are deterministic for same input.

Tasks:
- Add chunk planner service.
- Implement month key generation from timestamps.
- Add optional max-message secondary split.
- Add unit tests with boundary timestamps.

Dependencies:
- Issue 3.

Labels:
- feature
- ios
- backend

## Milestone 3: Compression + Encryption

### Issue 5: Add zstd compression adapter with benchmarks
Description:
- Add zstd adapter tuned for fast decompression in scroll path.
- Compression must reduce storage without hurting load latency.

Acceptance Criteria:
- Compression/decompression roundtrip works for chunk payloads.
- Benchmarks produce size + timing metrics.
- Adapter exposes configurable level with safe default.

Tasks:
- Integrate zstd library dependency.
- Implement `compress(data:)` and `decompress(data:)` APIs.
- Add benchmark helper for representative payload sizes.
- Add unit tests for corruption handling.

Dependencies:
- Issue 4.

Labels:
- feature
- ios
- performance
- backend

### Issue 6: Add AES-GCM archive encryptor and key derivation strategy
Description:
- Encrypt compressed blobs using AES-GCM with per-archive nonce.
- Archives must be unusable without device-protected keys.

Acceptance Criteria:
- Encryption and decryption succeed with valid key.
- Nonce is unique per archive write.
- Wrong key fails decryption.

Tasks:
- Define key provider interface using secure storage.
- Implement AES-GCM helper for archive payloads.
- Serialize archive as `[nonce | ciphertext | tag]`.
- Add security unit tests for wrong-key behavior.

Dependencies:
- Issue 5.

Labels:
- feature
- ios
- security
- backend

## Milestone 4: Storage Integration

### Issue 7: Implement file-based cold archive repository
Description:
- Persist encrypted archive files to app-local storage by thread and period.
- Required to move old messages out of hot SQLite storage.

Acceptance Criteria:
- Files written to `archives/<threadId>/<chunk>.arc`.
- Read, overwrite-protect, and delete APIs are available.
- No plaintext payload is persisted at rest.

Tasks:
- Implement archive path resolver.
- Add atomic write operation.
- Add read and integrity checks.
- Add tests for missing/corrupt files.

Dependencies:
- Issue 6.

Labels:
- feature
- ios
- backend
- security

### Issue 8: Add archive_index table and DAO queries
Description:
- Track archived ranges using SQLite index table.
- Enables fast lookups during scroll and consistency checks.

Acceptance Criteria:
- Migration creates `archive_index(thread_id, chunk_id, start_ts, end_ts)`.
- DAO supports insert, range query, and delete.
- Migration and DAO tests pass.

Tasks:
- Add DB migration script.
- Add DAO methods and indexes.
- Add integration tests with seeded data.

Dependencies:
- Issue 7.

Labels:
- feature
- ios
- backend

### Issue 9: Add archival transaction flow (write archive, delete hot rows, update index)
Description:
- Implement the core archival transaction pipeline.
- Prevents duplicate or missing messages during movement from hot to cold storage.

Acceptance Criteria:
- Successful run: archive file written, hot rows deleted, index inserted.
- Failure rollback leaves hot storage intact.
- Idempotent retry behavior is documented and tested.

Tasks:
- Add transactional orchestration in ArchiveManager.
- Implement failure handling and retry safety.
- Add integration tests for success/failure paths.

Dependencies:
- Issue 8.

Labels:
- feature
- ios
- backend
- security

## Milestone 5: Read Path (UI Integration)

### Issue 10: Detect archive gaps in conversation data source
Description:
- Update message data source to detect missing historical regions.
- Needed to trigger archive load when user scrolls into older ranges.

Acceptance Criteria:
- Data source identifies missing range with thread + timestamp bounds.
- Gap events are emitted once per range.
- Existing non-archive behavior is unchanged.

Tasks:
- Add gap detection in timeline query layer.
- Add event callback for archive loader.
- Add tests for repeated scroll behavior.

Dependencies:
- Issue 9.

Labels:
- feature
- ios
- backend

### Issue 11: Implement asynchronous archive chunk load and decode path
Description:
- Load, decrypt, decompress, and map archived chunks off the main thread.
- Prevents UI jank during historical scroll.

Acceptance Criteria:
- Pipeline executes on background queue.
- Main thread only receives ready-to-render message objects.
- Failure state is surfaced without blocking UI.

Tasks:
- Build async loader service.
- Add decrypt/decompress/map pipeline stages.
- Add cancellation support on rapid scroll.
- Add latency tests for chunk load.

Dependencies:
- Issue 10.

Labels:
- feature
- ios
- performance
- backend

### Issue 12: Merge archived messages into timeline renderer
Description:
- Insert restored messages into existing render pipeline preserving order.
- Ensures user sees continuous chat history.

Acceptance Criteria:
- Restored messages appear in correct order and grouping.
- Duplicate prevention works when hot and cold overlap.
- Scrolling remains responsive.

Tasks:
- Add merge policy for restored chunks.
- Implement dedupe by message identifier.
- Add UI/integration tests for continuity.

Dependencies:
- Issue 11.

Labels:
- feature
- ios
- performance

## Milestone 6: Background Jobs

### Issue 13: Add background archiving scheduler with safe triggers
Description:
- Run archive job when app is idle, charging, and low CPU.
- Prevents foreground performance regressions.

Acceptance Criteria:
- Job only starts when configured conditions are met.
- Job aborts cleanly when app state changes.
- Last-run telemetry is recorded.

Tasks:
- Integrate scheduler with iOS background task APIs.
- Implement trigger checks (idle/charging/resource).
- Add logging and state persistence.
- Add tests with mocked device state.

Dependencies:
- Issue 9.

Labels:
- feature
- ios
- performance
- backend

### Issue 14: Implement archive job throttling and backoff
Description:
- Add rate controls and retry policy for failed archival runs.
- Prevents repeated heavy work or battery drain.

Acceptance Criteria:
- Throttle limit per run window is enforced.
- Exponential backoff applies on repeated failures.
- Metrics include retry count and failure reason.

Tasks:
- Add throttle store and retry policy module.
- Integrate with scheduler and ArchiveManager.
- Add unit tests for retry schedule progression.

Dependencies:
- Issue 13.

Labels:
- feature
- ios
- performance
- backend

## Milestone 7: Testing + Benchmarking

### Issue 15: Add end-to-end archive-restore parity tests
Description:
- Verify archival + restoration yields identical text messages and order.
- This is the primary correctness requirement.

Acceptance Criteria:
- E2E test archives messages then restores exact payload and order.
- Tests cover multi-chunk and boundary timestamps.
- Wrong-key behavior is validated.

Tasks:
- Build deterministic fixture dataset.
- Add archive->restore E2E suite.
- Add expected-order assertions.

Dependencies:
- Issue 12.

Labels:
- feature
- ios
- backend
- security

### Issue 16: Add performance benchmark suite for compression and read latency
Description:
- Measure archive write/read costs and verify decompression target.
- Needed to validate product-quality UX before rollout.

Acceptance Criteria:
- Reports include compression ratio and load latency per chunk.
- Decompression target under 50 ms/chunk is tracked.
- Baseline report is committed as artifact.

Tasks:
- Add benchmark harness and representative datasets.
- Capture metrics for multiple chunk sizes.
- Export markdown/csv report for PR review.

Dependencies:
- Issue 15.

Labels:
- performance
- ios
- backend

### Issue 17: Add security validation checklist and plaintext leakage tests
Description:
- Verify no plaintext persistence and archive unreadability without keys.
- Required for secure storage-layer optimization.

Acceptance Criteria:
- Automated checks confirm no plaintext in archive files.
- Key access is scoped to secure store.
- Security review checklist is completed.

Tasks:
- Add test scanning archive artifacts for known plaintext strings.
- Validate key lifecycle boundaries.
- Document threat model assumptions.

Dependencies:
- Issue 15.

Labels:
- security
- ios
- backend

## Milestone 8: Polish + Feature Flag

### Issue 18: Add UX polish for archived-region loading states
Description:
- Improve user feedback while archived chunks are loading.
- Keeps behavior transparent without UI jitter.

Acceptance Criteria:
- Loading indicator appears only when needed.
- Error/retry states are user-safe and non-intrusive.
- No visible regressions in normal timeline.

Tasks:
- Add lightweight loading placeholder row.
- Add error retry affordance.
- Add UI snapshot tests.

Dependencies:
- Issue 12.

Labels:
- feature
- ios
- performance

### Issue 19: Finalize feature flag rollout and kill-switch playbook
Description:
- Define staged rollout and instant rollback path.
- Ensures safe production adoption.

Acceptance Criteria:
- Gradual rollout plan documented.
- Kill-switch procedure tested in staging.
- Monitoring dashboard links included.

Tasks:
- Configure staged exposure strategy.
- Add runtime toggle verification tests.
- Document rollback steps and ownership.

Dependencies:
- Issue 18.

Labels:
- feature
- ios
- backend

## Suggested Milestone Order and Exit Conditions

- Milestone 1 exits when compile-safe scaffolding and contracts are merged.
- Milestone 2 exits when ArchiveManager + chunk planner are deterministic.
- Milestone 3 exits when compression and encryption pass roundtrip + wrong-key tests.
- Milestone 4 exits when transactional archival pipeline is reliable.
- Milestone 5 exits when archived scroll path renders without blocking.
- Milestone 6 exits when background jobs are safe and throttled.
- Milestone 7 exits when parity, performance, and security evidence is published.
- Milestone 8 exits when feature is rollout-ready with kill switch.
