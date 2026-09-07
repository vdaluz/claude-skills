# reprioritize-backlog: rationale

Background for the rules in SKILL.md. Not required reading to run the skill - each rule in
SKILL.md is self-contained; this file is for understanding *why* a rule is shaped the way it is.

## Why description_html is fetched here, and why --limit doesn't shrink this call

Including `description_html` in Step 2's fetch costs more on that one call, but it avoids a
separate retrieve per tied issue in Step 4 - and ties are the normal case there, not an edge
case, so paying once up front is cheaper than paying per-tie later.

`--limit` applies client-side, after Step 2's fetch completes. That means a large backlog's full
`description_html` still gets pulled once during Step 2 even when `--limit` is small - the
file/`jq` fallback in Step 2 already covers the payload-size case, so `--limit` isn't a second
lever for shrinking that particular call.

## Why age can't be the default tie-break (Step 4)

A 3+-way tie on composite score is not a rare edge case - it's the normal outcome whenever
priority labels are mostly uniform (a backlog where everything got triaged as `low`) and no
Plane relations are recorded (most projects don't use them), which is common. Falling straight
to age in that case makes the entire pass a no-op relabeled as analysis: the output is just
"current creation order," dressed up as a reprioritization. Reading each tied issue's actual
content and ranking by judgment is what makes the tie-break add real information instead of
just restating what Plane's UI already shows by default.

## Why check #1 is blind to uniform-priority backlogs (Step 5)

Step 5's check #1 (score vs. stored priority) is structurally blind whenever a large share of
in-scope issues (roughly a third or more) already share one stored priority - the composite
score is partly *derived from* that same stored value, so a stale-but-uniform label can never
produce a mismatch by comparison alone. Reordering the pile without ever revisiting the label
just leaves every issue's `priority` field saying "these are all equally urgent" forever, which
quietly breaks any other tooling that reads `priority` as a signal (a "what's next" listing, a
next-issue picker) - they'll keep treating a fully-scoped, low-effort, live bug fix as identical
in urgency to an undetailed one-line idea note, because nothing ever told Plane otherwise. That's
why check #2 exists as a separate mechanism rather than relying on check #1 to eventually catch
uniform-priority drift on its own.
