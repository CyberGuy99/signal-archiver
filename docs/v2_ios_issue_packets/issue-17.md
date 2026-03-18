# Issue 17: Add security validation checklist and plaintext leakage tests

- Milestone: Milestone 7: Testing + Benchmarking
- Source Plan: docs/v2_ios_github_issues.md
- Dependencies: Issue 15
- Labels: feature, backend, ios

## Why
This packet tracks implementation details, test evidence, and commit history for Issue 17.

## Implementation Checklist
- [x] Confirm dependency issues are complete.
- [x] Implement scoped code changes in the Signal iOS fork.
- [x] Add/adjust tests for acceptance criteria.
- [x] Record benchmark/security outputs where applicable.
- [x] Update this file with concrete evidence and notes.

## Acceptance Criteria Snapshot
Refer to docs/v2_ios_github_issues.md for the canonical acceptance criteria for Issue 17.

## Evidence
- Branch/commit: Signal-iOS-Archive v2_ios @ c18a670acd (Issue 17: add archive security validation checks)
- Test command(s): Not executed in this Linux workspace for iOS target; intended macOS command: xcodebuild -workspace Signal.xcworkspace -scheme Signal -destination 'platform=iOS Simulator,name=iPhone 15' test
- Test result summary: Pending macOS/Xcode execution for iOS tests. Prototype regressions were previously run in signal-archiver (python -m unittest discover -s tests -p 'test_signal_archiver.py'): 5/5 passed.
- Notes: This issue packet was backfilled from branch history after implementation completed and was pushed.
