# CLAUDE.md — Guidance for AI Assistants

## Project Overview

Open Machine Foundation is a **documentation-only repository** — no code, no build system, no tests, no CI/CD. It tracks real-world incidents of AI agent misconduct, publishes governance principles for responsible machine deployment, and campaigns for transparent AI agent operation. All content is Markdown. Licensed under CC BY 4.0.

## Repository Structure

| File | Purpose | Maintained by |
|------|---------|---------------|
| `README.md` | Project overview, incident categories, and how the automation works | Human |
| `incident_inventory.md` | Living inventory of documented AI agent incidents | Automated (GitHub Actions + Claude) + Human |
| `contributing.md` | Contribution guidelines for human contributors | Human |
| `problem.md` | Academic essay: "When Machines Express Belief Faster Than Minds Can Think" | Human (authored essay) |
| `solution.md` | 14-principle manifesto for machine participation and truth protection | Human (authored essay) |
| `rulebook.md` | Plain-language guide to the manifesto with compliance examples | Human |
| `case-study.md` | Deep-dive case study of the MJ Rathbun incident | Human (authored essay) |
| `.github/workflows/incident-tracker.yml` | GitHub Actions workflow for daily incident scanning | Human |
| `scripts/scan_incidents.py` | Python script using Anthropic API with web search | Human |

## Document Relationships

`problem.md` diagnoses the philosophical crisis of truth in the age of autonomous agents. `solution.md` proposes governance principles to address it. `rulebook.md` translates those principles into plain language with practical industry examples. `case-study.md` grounds the analysis in a real incident. `incident_inventory.md` is the living evidence base that supports the entire project. `contributing.md` and `README.md` are operational documents.

## Writing Conventions

- **Neutral, academic tone** throughout — no editorialising, no emotional language, no advocacy
- **British English spelling** — licence, behaviour, recognised, analysed, unauthorised, defence, etc.
- **Third person** for incident descriptions
- **Factual claims only** — no speculation about motives or outcomes not supported by sources
- When describing incidents: state what happened, the impact, and cite the source — nothing more

## Incident Entry Format

The incident log in `incident_inventory.md` uses this exact table format:

```
| Date | Title | Category | Severity | What Happened | Impact | Source |
```

- **Date:** `YYYY-MM` or `YYYY-MM-DD`
- **Title:** Short descriptive name, no editorialising
- **Category:** One of — `Retaliation`, `User Harm`, `Platform Security`, `Supply Chain`, `Financial Fraud`, `Enterprise Infiltration`, `Content Degradation`
- **Severity:** `Critical`, `High`, or `Medium` (refer to the severity assessment table at the bottom of the inventory for guidance)
- **What Happened:** 2–3 sentences, factual, neutral
- **Impact:** Brief statement of who was affected and how
- **Source:** Linked source names in markdown format `[Name](URL)`
- New incidents are **appended to the bottom** of the incident log table
- **No duplicate entries** — check the existing inventory first
- If updating an existing entry, modify it in place rather than adding a new row

## Source Requirements

- All incidents must cite **credible sources**: established news outlets, security research firms, official advisories, or verified first-person accounts
- Forum posts and social media alone are not sufficient unless corroborated
- Multiple sources are preferred for Critical and High severity incidents

## Automation Context

- `incident_inventory.md` is scanned for updates **daily at 07:00 UTC** by a GitHub Actions workflow (`.github/workflows/incident-tracker.yml`)
- The workflow runs `scripts/scan_incidents.py`, which calls the Anthropic API (Claude with web search) to find new incidents
- Updates are proposed as **pull requests** for human review — never committed directly to `main`
- The workflow can also be triggered manually via `workflow_dispatch`
- Requires the `ANTHROPIC_API_KEY` repository secret to be configured
- Human-verified information **takes precedence** over automated scans
- When editing `incident_inventory.md`, check for open automated PRs on the `auto/incident-update` branch to avoid conflicts
- Do not modify the "Scale of the Problem" metrics table, "Severity Assessment" table, or "Key Finding" section without explicit instruction — these are curated summaries

## Commit Message Convention

- Action-oriented, verb-first (e.g. "Add new incident entry for…", "Update severity assessment…", "Revise incident description…")
- Clear and descriptive — state what changed
- No conventional commit prefixes (`feat:`, `fix:`, etc.)

## Do Not

- Add speculative or unverified incidents
- Editorialise or add opinion to any document
- Modify `problem.md`, `solution.md`, or `case-study.md` without explicit instruction — these are authored essays, not living documents
- Restructure the incident table format or severity assessment
- Remove or modify source citations without providing replacement sources
