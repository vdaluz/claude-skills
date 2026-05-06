Critically review a plan, code, or diff and surface real issues.

Arguments: what to roast (plan / code / diff) and the content to review (pasted or pointed to).

Be blunt and direct. No softening. Prioritize by severity.

## Checklist

**Correctness**
- Does it actually solve the stated problem?
- Are there steps that won't work as written?
- Are assumptions stated explicitly — and are they valid?

**Rule and process violations**
- Does it follow documented project conventions (CLAUDE.md, runbooks, state schema)?
- Does it skip required steps (validation, deployment, verification)?
- Does it create files/docs without authorization?

**Completeness**
- Are there missing steps that would cause it to fail?
- Is verification (system-level AND user-facing) included?
- Are rollback/recovery steps present where needed?

**Scope creep / over-engineering**
- Does it do more than asked?
- Are there unnecessary abstractions, scripts, or docs being created?
- Is there a simpler approach that would work just as well?

**Security and safety**
- Does it expose credentials, IPs, or internal hostnames?
- Does it run destructive commands without guards?
- Does it bypass validation or safety checks?

**Edge cases and failure modes**
- What happens if the target host is unreachable?
- What happens if a step fails halfway through?
- Are there race conditions or ordering dependencies?

## Output format

1. **Verdict**: ready / needs work / start over (one line, up front)
2. **Critical issues** (would cause failure or data loss): list with exact fix for each
3. **Significant issues** (would cause bugs or rule violations): list with exact fix
4. **Minor issues** (style, efficiency, completeness): brief list
5. If "start over": say why and what the correct approach is
