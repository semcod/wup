# Repository agent instructions

<!-- wellmanifest:docs-placement:start -->
## Documentation placement

WUP adopts the layout and document contract of
[wellmanifest/docs 0.1.1](https://github.com/wellmanifest/docs/blob/ebe7501063ef4f3e63ded610c2d3183010ca636e/docs/standard/POLICY.md)
at immutable revision `ebe7501063ef4f3e63ded610c2d3183010ca636e`.
The local adoption pin is `.governance/docs.json`.

Before writing a durable result, identify its owner, kind and canonical path:

- durable information: `docs/information/<id>.md`;
- analysis: `docs/analysis/<id>.md`;
- refactoring plan: `docs/refactoring/<id>.md`;
- architecture decision: `docs/decisions/<id>.md`.

Use a stable identifier, JSON metadata, the required `docs:section` markers
and an entry in `docs/README.md`. A Planfile ticket contains bounded intent
and links to the canonical document; `project/ticket-*`, chat, cache and
temporary directories are not the only location of a delivered result.

This declared adoption has local checker coverage only. It does not claim a
deployed protected OneDev gate, successful canary, merge authority or a full
Wellmanifest fleet profile. Add the checker to the existing protected local CI
only through the governed deployment process.
<!-- wellmanifest:docs-placement:end -->

<!-- wellmanifest:local-ci-publication:start -->
## Local CI and independent publication

Adopt the publication policy from [Wellmanifest/new-project 0.20.10](https://github.com/wellmanifest/new-project/blob/d5f77d83b3752477cfb95a535d0e1ce77f148576/docs/information/local-ci-publication.md).
Immutable source revision: `d5f77d83b3752477cfb95a535d0e1ce77f148576`.
Document SHA-256: `44803480f1d51f64eec81a62335b6725747f01b5f2de78105ebfc4017a7922c6`.
This is publication-policy adoption; it does not establish full governance,
adoption of every Wellmanifest pack, deployed CI or successful verification.

For `semcod/*` and `subactor/*`, prefer the protected local OneDev executor
and independent local Validator App. Preserve the repository's own tests,
required platform matrix, protected checks and actor boundaries. Read the
actual protected Validator profile and OneDev configuration; missing profiles
are coverage gaps. GitHub may host code and PRs without hosting test execution.
A GitHub Actions billing/capacity failure does not prove local CI is unavailable.

Before publication, observe existing local reconciliation and reuse its receipt.
Require verification of the exact PR head with the current base and merge result.
Invoke the trusted local Validator adapter or its existing timer under the
user's publication authorization; never self-approve or merge directly.
Use hosted `dispatch-direct-pr.sh` only when the protected deployment explicitly
selects that transport. This rule supersedes older unconditional hosted-dispatch
examples, while retaining all additional repository requirements.

Retire a hosted check only after equivalent local tests and the required OS
matrix have a successful deployed canary and an independently reviewed policy
migration. Never empty required checks or create synthetic success statuses.
Report declared, configured, deployed, verified and published evidence separately.
The complete fleet audit belongs in `subactor/docs/architecture/analysis/local-ci-adoption.md`.
<!-- wellmanifest:local-ci-publication:end -->
