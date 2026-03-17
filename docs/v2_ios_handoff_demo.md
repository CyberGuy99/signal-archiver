# V2 iOS Handoff and Demo Runbook

This runbook is for an engineer with Xcode access to demonstrate the V2 storage-layer archive feature in a Signal iOS fork.

## Objective

Demonstrate that old text messages can be moved from hot DB storage into encrypted compressed archives and loaded back during scroll with no protocol change.

## Scope Guardrails

- No Signal protocol modifications.
- No message encryption scheme changes.
- Storage-layer optimization only.
- Local device archiving only (no cross-device archive sync).

## Environment Prerequisites

- macOS with latest stable Xcode.
- iOS Simulator and/or test iPhone.
- Signal iOS fork checked out on branch `v2_ios` (or downstream branch).
- Ability to run unit + integration tests in Xcode.
- zstd dependency integrated for iOS target.

## Implementation Map

Use the issue backlog in [docs/v2_ios_github_issues.md](docs/v2_ios_github_issues.md).

Target modules in iOS codebase:
- Storage layer: ArchiveManager + DAO + repository.
- Database migrations: `archive_index` table.
- Background scheduler: idle/charging/low-resource checks.
- Chat timeline data source: gap detection + async chunk load.

## Suggested File/Module Ownership

- ArchiveManager.swift: orchestration for archive/write/read.
- ArchiveChunker.swift: month + count based chunk planning.
- ArchiveCompression.swift: zstd adapter.
- ArchiveEncryption.swift: AES-GCM helper + key provider.
- ArchiveRepository.swift: file read/write in app-private directory.
- ArchiveIndexDAO.swift: DB table operations.
- TimelineArchiveLoader.swift: async load/decrypt/decompress/map.
- FeatureFlags.swift: runtime and build guards.

## Demo Dataset Preparation

- Create a synthetic chat thread with at least 20k text messages spanning >= 6 months.
- Ensure message timestamps cross month boundaries.
- Include a repeated dictionary (common words) to show compression effect.

## Demo Steps (Live)

1. Start app with feature flag OFF.
2. Open target thread and verify baseline behavior.
3. Turn feature flag ON in staging/debug config.
4. Trigger archive job manually (debug menu or developer command).
5. Confirm old messages removed from hot storage range.
6. Confirm archive files exist in app sandbox and are encrypted.
7. Scroll into archived period.
8. Observe asynchronous chunk load and message rendering.
9. Verify message ordering and continuity.
10. Toggle feature OFF and verify fallback behavior remains stable.

## Evidence to Collect

- Before/after storage size snapshot (DB and archive folder).
- Compression ratio report per chunk size.
- Read latency report, including per-chunk decompression time.
- Screen recording of smooth archive-region scrolling.
- Security checks: wrong-key failure and no plaintext at rest.

## Validation Checklist

Functional:
- Archive -> restore returns identical text payloads.
- Message order preserved across hot/cold boundary.
- No duplicate messages when chunks merge into timeline.

Performance:
- Decompression under 50 ms/chunk target.
- No frame drops during archived-region scroll on target device tier.

Security:
- Archive files are unreadable without valid key.
- No plaintext chunk artifacts on disk.
- Key material stays in approved secure storage boundary.

## If iPhone Demo Is Not Possible

Provide handoff package to Xcode owner with:
- Branch name and commit SHA.
- Completed issue checklist from [docs/v2_ios_github_issues.md](docs/v2_ios_github_issues.md).
- Test command list (unit/integration/perf).
- Demo script steps from this runbook.
- Known limitations and open risks.

## PR Checklist for Xcode Owner

- Link all completed issues to PR.
- Include benchmark report files and screenshots.
- Include migration and rollback notes.
- Include feature flag rollout plan and kill switch validation.
- Request security review sign-off before merge.
