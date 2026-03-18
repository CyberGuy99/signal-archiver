# Issue 1: Add V2 archive feature flag scaffold

- Milestone: Milestone 1: Project Setup
- Source Plan: docs/v2_ios_github_issues.md
- Dependencies: None
- Labels: feature, backend, ios

## Why
This packet tracks implementation details, test evidence, and commit history for Issue 1.

## Implementation Checklist
- [x] Confirm dependency issues are complete.
- [x] Implement scoped code changes in the Signal iOS fork.
- [x] Add/adjust tests for acceptance criteria.
- [x] Record benchmark/security outputs where applicable.
- [x] Update this file with concrete evidence and notes.

## Acceptance Criteria Snapshot
Refer to docs/v2_ios_github_issues.md for the canonical acceptance criteria for Issue 1.

## Evidence
- Branch/commit: Signal-iOS-Archive v2_ios @ ed9ee55f04 (Issue 1: add chat archive v2 compile/runtime flags)
- Test command(s): Not executed in this Linux workspace for iOS target; intended macOS command: xcodebuild -workspace Signal.xcworkspace -scheme Signal -destination 'platform=iOS Simulator,name=iPhone 15' test
- Test result summary: Pending macOS/Xcode execution for iOS tests. Prototype regressions were previously run in signal-archiver (python -m unittest discover -s tests -p 'test_signal_archiver.py'): 5/5 passed.
- Notes: This issue packet was backfilled from branch history after implementation completed and was pushed.
