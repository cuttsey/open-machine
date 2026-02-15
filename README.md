# Open Machine Foundation
Open Machine tracks incidents of AI agent harm, publishes governance principles for responsible machine deployment, and campaigns for a future where AI agents operate openly or not at all.

# AI Agent Incident Tracker

An open, transparent, and automatically maintained inventory of documented incidents involving autonomous AI agents — with a particular focus on the OpenClaw/Moltbook ecosystem.

## Purpose

This repository tracks real-world cases where autonomous AI agents have caused harm, including reputational attacks, security breaches, financial fraud, supply chain compromise, and enterprise infiltration. It was created in response to the [MJ Rathbun incident](https://theshamblog.com/an-ai-agent-published-a-hit-piece-on-me/) of February 2026, in which an OpenClaw AI agent autonomously published a defamatory attack piece against a matplotlib maintainer who rejected its code contribution.

The inventory is maintained automatically by a daily n8n workflow that uses Claude (Anthropic's AI) with web search to scan for new incidents, then commits updates directly to this repository. Every change is visible in the Git history.

## How It Works

1. **Daily at 07:00 UTC**, an n8n scheduled workflow fires.
2. The workflow fetches the current `incident_inventory.md` from this repository via the GitHub API.
3. It calls Claude (Sonnet 4.5) with web search enabled, instructing it to find new incidents since the last update.
4. If new incidents are found, the inventory is updated and committed back to this repository with a descriptive commit message.
5. If no new incidents are found, the workflow logs the result and takes no action.

All updates are attributed to the committer **AI Incident Tracker Bot** so they are clearly distinguishable from human edits.

## Files

| File | Description |
|------|-------------|
| `incident_inventory.md` | The living inventory of documented incidents |
| `README.md` | This file |
| `CONTRIBUTING.md` | Guidelines for human contributions |
| `LICENSE` | CC BY 4.0 — open for reuse with attribution |

## Incident Categories

The inventory tracks six categories of AI agent misconduct:

1. **Autonomous retaliation and reputational attacks** — agents targeting individuals who reject or oppose them
2. **Agents turning on their own users** — agents harming the people who deployed them
3. **Platform-level security disasters** — systemic failures in agent hosting infrastructure
4. **Malicious skill/plugin supply chain attacks** — compromised agent extensions
5. **Financial fraud and cryptocurrency exploitation** — agent-enabled scams
6. **Enterprise infiltration ("Shadow AI")** — unauthorised agent deployment in corporate environments

## Contributing

Human contributions are welcome and encouraged. See `CONTRIBUTING.md` for guidelines. If you have knowledge of an incident not yet listed, please open a pull request or an issue.

## Context

This tracker was created alongside a set of academic and policy documents:

- **"Truth at Machine Speed"** — an academic essay examining philosophical theories of truth (Kant, Habermas, Rorty) in relation to autonomous AI agents
- **"A Manifesto for Machine Participation and the Protection of Truth"** — a set of 14 governance principles for AI agent deployment
- **"Open Machine Principles"** — a plain-language guide to the manifesto with industry compliance examples

## Licence

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt this material for any purpose, provided you give appropriate attribution.
