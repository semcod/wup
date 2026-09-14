# ticket-003: TestQL-to-Planfile incident automation

- **Status**: COMPLETE
- **Workflow state**: VALIDATION

SESSION_EXECUTION_AUTHORIZATION: the user requested that this change be pushed,
merged and tested.

AC-01: WUP runs the maintained TestQL scenarios as periodic probes with a
realistic timeout.
AC-02: A detected failure creates one deduplicated ticket explicitly marked for
GitHub synchronization.
AC-03: Recovery completes the matching ticket and retains deduplication when
completion fails.
AC-04: Local watcher state is ignored by Git, while non-secret GitHub target
configuration is versioned.
AC-05: The persistent user service is documented and verified.

GitHub issue: https://github.com/semcod/wup/issues/4
