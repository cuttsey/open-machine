#!/usr/bin/env python3
"""Scan for new AI agent incidents and update the inventory.

Uses the Anthropic API with web search to find new incidents of AI agent
misconduct, then updates incident_inventory.md with any new entries.
Designed to run in GitHub Actions and produce a PR for human review.
"""

import os
import sys
import logging
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
    logging.basicConfig(level=logging.INFO)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logging.error("ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    # Read the current inventory file
    inventory = INVENTORY_PATH.read_text(encoding="utf-8")

    # Choose model via env var so CI/workflows can change it without editing code
    MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-2")

    logging.info("Using Anthropic model: %s", MODEL)

    client = anthropic.Anthropic(api_key=api_key)

    logging.info("Searching for new AI agent incidents...")

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
            messages=[{"role": "user", "content": USER_PROMPT_TEMPLATE.format(inventory=inventory)}],
        )
    except Exception as e:
        # Prefer catching the anthropic-specific NotFoundError when model is missing
        try:
            NotFound = getattr(anthropic, "NotFoundError", None)
        except Exception:
            NotFound = None

        if NotFound is not None and isinstance(e, NotFound):
            logging.error("Anthropic model '%s' was not found: %s", MODEL, e)
            logging.error("Set the ANTHROPIC_MODEL environment variable in CI to a model you have access to (eg 'claude-2').")
            sys.exit(2)

        # Fallback: string-match common not-found messages
        msg = str(e).lower()
        if "not_found" in msg or ("model" in msg and "not found" in msg):
            logging.error("Anthropic model '%s' was not found: %s", MODEL, e)
            logging.error("Set the ANTHROPIC_MODEL environment variable in CI to a model you have access to (eg 'claude-2').")
            sys.exit(2)

        # Other errors => fail hard so CI surfaces the problem
        logging.exception("Anthropic API request failed: %s", e)
        sys.exit(1)

    # The client returns an iterable of content blocks; join text blocks.
    result_text = ""
    for block in response.content:
        if getattr(block, "type", None) == "text":
            result_text += getattr(block, "text", "")

    result_text = result_text.strip()

    if result_text == "NO_NEW_INCIDENTS" or not result_text:
        logging.info("No new incidents found.")
        sys.exit(0)

    # Update the inventory file
    INVENTORY_PATH.write_text(result_text + "\n", encoding="utf-8")

    # Update the last-updated date if present; be defensive in case format changed
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        updated = INVENTORY_PATH.read_text(encoding="utf-8")
        if "**Last updated:** " in updated:
            old_date = updated.split("**Last updated:** ")[1].split("\n")[0]
            updated = updated.replace(old_date, today, 1)
            INVENTORY_PATH.write_text(updated, encoding="utf-8")
        else:
            logging.warning("Could not find '**Last updated:**' in inventory; skipping date update.")
    except Exception:
        logging.exception("Failed to update 'Last updated' date in inventory; continuing.")

    logging.info("Inventory updated with new incidents. Last updated set to %s.", today)

    # Signal to the workflow that changes were made
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        try:
            with open(github_output, "a") as f:
                f.write("has_changes=true\n")
        except Exception:
            logging.exception("Failed to write GITHUB_OUTPUT; CI may not detect changes.")


if __name__ == "__main__":
    main()
