#!/usr/bin/env python3
"""Scan for new AI agent incidents and update the inventory.

Uses the Anthropic API with web search to find new incidents of AI agent
misconduct, then updates incident_inventory.md with any new entries.
Designed to run in GitHub Actions and produce a PR for human review.
"""

import os
import sys
from pathlib import Path

import anthropic

INVENTORY_PATH = Path(__file__).resolve().parent.parent / "incident_inventory.md"

SYSTEM_PROMPT = """\
You are an AI incident researcher for the Open Machine Foundation. Your job is \
to find new, credible incidents of AI agent misconduct and update the incident \
inventory.

Rules:
- Use web search to find incidents reported since the last update date.
- Only include incidents backed by credible sources (established news outlets, \
security research firms, official advisories, verified first-person accounts).
- Do not include speculative or unverified incidents.
- Write in neutral, academic British English. No editorialising.
- Use third person for incident descriptions.
- Categories: Retaliation, User Harm, Platform Security, Supply Chain, \
Financial Fraud, Enterprise Infiltration, Content Degradation.
- Severity: Critical, High, or Medium.
- Date format: YYYY-MM or YYYY-MM-DD.
- Source format: [Name](URL) with real, verified URLs.
- Do not duplicate incidents already in the inventory.
- Do not modify existing entries, the Scale of the Problem table, the Severity \
Assessment table, or the Key Finding section.

If no new incidents are found, respond with exactly: NO_NEW_INCIDENTS
"""

USER_PROMPT_TEMPLATE = """\
Here is the current incident inventory:

<inventory>
{inventory}
</inventory>

Search the web for new AI agent misconduct incidents that have been reported \
since the last update date shown in the inventory. Focus on:
- Autonomous AI agents causing harm (retaliation, security breaches, fraud, etc.)
- AI agent platform vulnerabilities and exploits
- Supply chain attacks via AI agent plugins/skills
- Enterprise shadow AI incidents
- AI agents turning on their users
- Content degradation caused by AI agents

If you find new incidents, return the COMPLETE updated inventory file with the \
new entries appended to the bottom of the Incident Log table. Return ONLY the \
raw markdown content of the file — no code fences, no commentary.

If no new credible incidents are found, respond with exactly: NO_NEW_INCIDENTS
"""


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    inventory = INVENTORY_PATH.read_text(encoding="utf-8")

    client = anthropic.Anthropic(api_key=api_key)

    print("Searching for new AI agent incidents...")

    response = client.messages.create(
        model="claude-sonnet-4-6-20250514",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
        messages=[{"role": "user", "content": USER_PROMPT_TEMPLATE.format(inventory=inventory)}],
    )

    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text += block.text

    result_text = result_text.strip()

    if result_text == "NO_NEW_INCIDENTS" or not result_text:
        print("No new incidents found.")
        sys.exit(0)

    # Update the inventory file
    INVENTORY_PATH.write_text(result_text + "\n", encoding="utf-8")

    # Update the last-updated date
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    updated = INVENTORY_PATH.read_text(encoding="utf-8")
    updated = updated.replace(
        updated.split("**Last updated:** ")[1].split("\n")[0],
        today,
    )
    INVENTORY_PATH.write_text(updated, encoding="utf-8")

    print(f"Inventory updated with new incidents. Last updated set to {today}.")
    # Signal to the workflow that changes were made
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write("has_changes=true\n")


if __name__ == "__main__":
    main()
