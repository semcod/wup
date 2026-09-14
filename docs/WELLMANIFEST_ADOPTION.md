# Wellmanifest adoption and delivery evidence

WUP adopts Wellmanifest as a process and validation standard. It is not a WUP
runtime dependency and must not be installed by the protected test lane.

## Immutable source

The repository adopts the local-CI publication policy from
[`wellmanifest/new-project` 0.20.10](https://github.com/wellmanifest/new-project/blob/d5f77d83b3752477cfb95a535d0e1ce77f148576/docs/information/local-ci-publication.md)
at revision `d5f77d83b3752477cfb95a535d0e1ce77f148576`. The adopted document
SHA-256 is `44803480f1d51f64eec81a62335b6725747f01b5f2de78105ebfc4017a7922c6`.
The executable policy is reproduced in [AGENTS.md](../AGENTS.md).

## Current evidence

| Layer | State | Evidence |
| --- | --- | --- |
| Declared | Present | The immutable publication policy in `AGENTS.md`. |
| Configured | Partial | `pyproject.toml` separates the locked `test` lane from optional `automation`; `Taskfile.yml` uses `uv`. |
| Deployed | Partial | OneDev has a WUP `check-locked-manifest.py` profile. It only accepts a fixed manifest digest and cannot validate application or dependency changes. |
| Verified | Local only | The isolated `test` lane completed 399 tests and Ruff. The current PR head is rejected by the limited OneDev profile with `LOCKED_MANIFEST_DEPENDENCY_PIN_MISMATCH`. |
| Published | Pending | No WUP change is merged on the basis of the limited profile. |

## Delivery plan

1. [GitHub issue #9](https://github.com/semcod/wup/issues/9) owns the protected
   OneDev profile: exact head/base/merge-result validation, a pinned wheelhouse,
   root Python 3.10+ coverage and workspace Python 3.11+ coverage.
2. [GitHub issue #8](https://github.com/semcod/wup/issues/8) and
   [issue #11](https://github.com/semcod/wup/issues/11) own Planfile lifecycle
   defects. The implementation is proposed in
   [semcod/planfile PR #80](https://github.com/semcod/planfile/pull/80).
3. [GitHub issue #10](https://github.com/semcod/wup/issues/10) owns the next
   adoption step: record the validation-attestation contract after the protected
   profile exists and demonstrate it with a canary.

A valid receipt must identify the repository, PR number, exact head SHA, base
SHA, computed merge result, profile digest, test matrix and validator identity.
A local test result, a Planfile ticket or this document cannot approve a merge.
