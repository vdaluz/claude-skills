---
name: create-prd
description: Create a PRD (Product Requirements Document) for a project or feature.
---

Create a PRD (Product Requirements Document) for a project or feature.

Arguments: project name or issue tracker identifier, feature/scope description (optional), target (issue tracker project page or markdown file path).

## What a PRD covers

- **Overview** — one paragraph: what this is, who it's for, why it exists now
- **Problem statement** — the pain being solved, with evidence or context
- **Goals** — 3–6 measurable outcomes; what success looks like
- **Non-goals** — explicit scope exclusions (prevents scope creep)
- **Users** — who uses this and their key needs/constraints
- **Functional requirements** — what the system must do (numbered, testable)
- **Non-functional requirements** — performance, security, reliability, compatibility constraints
- **Out of scope** — features or work explicitly deferred
- **Open questions** — unresolved decisions that need answers before or during build

## Steps

1. If a project identifier is given and you have the Plane MCP server available, call `mcp__plane__list_projects` to resolve the project ID.
2. If any key context is missing (what problem this solves, who the users are), ask before drafting. Do not invent scope.
3. Read relevant codebase context: existing CLAUDE.md files, README, any state/config files that reveal architecture or constraints.
4. Draft the PRD using the sections above. Be specific and concrete — avoid vague goals like "improve UX". Write requirements in testable language ("the system shall...").
5. Keep it lean: no padding, no filler transitions, no AI buzzwords. Each section earns its place.
6. Determine target:
   - **Plane project page** (default if Plane MCP is available): create via `mcp__plane__create_project_page` on the matching project. Title: "PRD: <feature or project name>".
   - **Markdown file**: write to the path given by the user (e.g. `docs/prd.md`). Only create a file if the user explicitly asked for one.
7. Output the target location (Plane page URL or file path) and a one-paragraph summary of the PRD's key decisions.

## Rules

- Never invent requirements. If scope is unclear, ask first or flag as an open question.
- Non-goals are mandatory — a PRD without them is incomplete.
- Open questions are mandatory — if you have none, you haven't thought hard enough.
- Do not create an issue for the PRD itself (a page is the right artifact, not an issue).
- If a PRD already exists for this project/feature, read it first and propose updating rather than duplicating.
