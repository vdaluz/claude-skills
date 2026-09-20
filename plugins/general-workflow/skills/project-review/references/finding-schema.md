# Run directory layout and finding schema

## Layout

```
.review/
  rejected.md                 findings the user declined in any run - feeds the next run's do-not-report list
  <YYYY-MM-DD>-<mode>/
    context.md                step 2 - facts only
    plan.md                   step 3 - evidence plan, including what was skipped or unavailable
    code/                     raw tool output: typecheck.txt, lint.txt, audit.json, secrets.txt, coverage.txt, build.txt ...
    design/                   routes.md, <route>--<viewport>--<theme>[--<state>].png, <route>.snapshot.md,
                              axe--<route>.json, targets--<route>.json, console--<route>.txt, lighthouse--<route>.json
    judged/<dimension>.md     verbatim judge replies
    judged/candidates.md      all candidates with ids, then refuter verdicts
    findings.md               the deliverable
```

## Finding format

One block per finding, exactly these fields:

```
### <id> - <title: imperative, specific, under 80 chars>
- dimension: <security | performance | architecture | maintainability | testing | dependencies | usability | accessibility | visual-consistency | feature-gap>
- severity: <critical | high | medium | low>
- confidence: <0-100>
- effort: <S | M | L>   (S: under half a day, M: up to two days, L: more)
- evidence: <path:line[, path:line...] | screenshot file + selector/region | tool-output file + entry>
- problem: <what is wrong, in terms of behavior - two or three sentences>
- impact: <who or what is affected, and when>
- proposed fix: <code: the concrete change. design: the direction, not a pixel spec>
- acceptance criteria: <one to three checkable statements>
```

## Severity

Unless the project's REVIEW.md redefines it:

- **critical** - exploitable security hole, data loss, or a core flow that cannot be completed.
- **high** - confirmed bug or barrier affecting real use; WCAG 2.2 A failure on a primary flow; a structural problem that blocks planned work.
- **medium** - real cost, no immediate breakage: a maintainability hotspot with evidence of churn, WCAG AA failure, measurable performance regression risk.
- **low** - cosmetic or minor; reported only if cheap and clearly right.

Severity is impact x likelihood. It is not raised to get attention, and it is independent of confidence.
