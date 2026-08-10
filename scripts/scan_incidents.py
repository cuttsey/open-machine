#!/usr/bin/env python3
"""Scan for new AI incidents and update the inventory.

Uses the Anthropic API with web search to find new, credible incidents
involving AI systems, AI agents, frontier models, model security, unexpected
AI behaviour, and AI-enabled or AI-mediated harm.

The scanner is intentionally model-, vendor-, and framework-agnostic. It should
capture incidents involving autonomous agents, foundation models, frontier
models, AI products, AI infrastructure, model supply chains, and unexpected
behaviour discovered during evaluation or deployment.

Designed to run in GitHub Actions and produce a PR for human review.
"""

import os
import sys
import traceback
from pathlib import Path
from datetime import datetime, timezone

import anthropic


INVENTORY_PATH = Path(__file__).resolve().parent.parent / "incident_inventory.md"


SYSTEM_PROMPT = """
You are an AI incident researcher for the Open Machine initiative.

Your job is to find new, credible incidents involving artificial intelligence
and update the incident inventory.

The inventory is intentionally broader than "AI agent misconduct". It covers
the full incident and failure surface of increasingly capable AI systems,
including foundation models, frontier models, autonomous agents, AI products,
AI infrastructure, model supply chains, evaluation environments, and
unexpected AI behaviour.

SCOPE

Look for credible incidents in any of the following areas:

1. UNEXPECTED OR CONCERNING AI BEHAVIOUR

- Unexpected autonomous behaviour
- Deceptive behaviour
- Strategic deception
- Situational awareness
- Attempts to evade monitoring or evaluation
- Attempts to manipulate users, operators, evaluators, or developers
- Self-preservation or resistance to shutdown
- Replication, persistence, or attempts to maintain access
- Goal misgeneralisation
- Unexpected pursuit of objectives
- Reward hacking
- Specification gaming
- Sandbagging or capability concealment
- Behaviour that changes materially when the model believes it is being
  evaluated
- Sabotage or attempted sabotage
- Attempts to undermine safety controls
- Unexpected tool use
- Unexpected external actions
- AI systems acting contrary to operator intent
- Other behaviour that researchers, developers, users, or credible observers
  reasonably describe as anomalous, concerning, or difficult to explain

2. FRONTIER MODEL INCIDENTS

Include incidents involving highly capable or frontier AI models, whether
publicly released, privately deployed, previewed, restricted, or under
evaluation.

Examples include, but are not limited to:

- Claude / Anthropic frontier systems
- OpenAI frontier systems
- Google DeepMind frontier systems
- Meta frontier systems
- xAI frontier systems
- Microsoft frontier systems
- DeepSeek frontier systems
- Qwen frontier systems
- Other leading or emerging frontier models

Named systems may include models such as Fable, Mythos, GPT-series systems,
Claude-series systems, Gemini-series systems, or future models not yet known
at the time this prompt was written.

Do NOT assume that an incident must involve a named agent framework.

3. MODEL BREACHES AND COMPROMISE

Include:

- Unauthorised access to restricted AI models
- Theft or exposure of model weights
- Theft or exposure of model checkpoints
- Leakage of restricted model capabilities
- Compromise of model-serving infrastructure
- Compromise of evaluation environments
- Compromise of model development infrastructure
- Compromise through contractors, vendors, partners, or third parties
- Supply-chain compromise affecting an AI model
- Credential theft leading to access to restricted AI systems
- Model extraction or capability extraction where materially significant
- Sandbox escapes
- Container escapes
- Isolation failures
- Network containment failures
- Jailbreaks with credible security significance
- Safety-control bypasses
- Classifier or guardrail bypasses where the resulting capability is
  materially significant
- Accidental public exposure of restricted systems or capabilities

4. AI AGENT INCIDENTS

Include autonomous or semi-autonomous systems causing or attempting to cause:

- Retaliation
- User harm
- Unauthorised actions
- Security breaches
- Credential theft
- Data exfiltration
- Fraud
- Financial loss
- Social engineering
- Phishing
- Impersonation
- Enterprise infiltration
- Persistence
- Lateral movement
- Unauthorised code execution
- Unauthorised communications
- Manipulation of users or organisations
- Attempts to circumvent human oversight

Do not restrict this category to OpenClaw or any other particular agent
framework.

5. AI-ENABLED SECURITY INCIDENTS

Include incidents where AI materially contributes to:

- Cyberattacks
- Vulnerability discovery and exploitation
- Malware development or deployment
- Phishing campaigns
- Credential attacks
- Identity attacks
- Data theft
- Cloud compromise
- Infrastructure compromise
- Automated reconnaissance
- Social engineering
- Fraud
- Extortion
- Disinformation or coordinated manipulation

Distinguish between ordinary AI-assisted activity and incidents where AI
materially changes the scale, speed, autonomy, effectiveness, or nature of
the attack.

6. AI SAFETY AND CONTROL FAILURES

Include:

- Failed safeguards
- Safety classifier failures
- Guardrail failures
- Monitoring failures
- Evaluation failures
- Misleading safety evaluations
- Capability overhang discovered after deployment
- Unexpected emergent capabilities
- Dangerous capabilities discovered unexpectedly
- Failures of human-in-the-loop controls
- Failures of containment
- Failures of sandboxing
- Failures of access control
- Failures of model governance
- Incidents demonstrating a meaningful gap between intended and observed
  behaviour

7. ENTERPRISE AND DEPLOYMENT INCIDENTS

Include:

- Shadow AI incidents
- AI systems making consequential unauthorised decisions
- AI systems causing material business disruption
- AI systems exposing confidential information
- AI systems accessing data beyond their intended permissions
- AI systems taking unintended actions in enterprise environments
- AI automation causing material operational, financial, legal, or reputational
  harm
- Unexpected behaviour in production systems
- Model updates causing unexpected regressions or dangerous behaviour

8. SUPPLY CHAIN AND INFRASTRUCTURE

Include:

- Compromised AI plugins
- Compromised AI skills
- Malicious tools
- Malicious MCP servers
- Compromised model providers
- Compromised inference providers
- Compromised datasets
- Poisoned training data
- Poisoned retrieval data
- Compromised packages or dependencies
- Compromised AI development environments
- Third-party vendor compromises affecting AI systems
- Dependency attacks
- AI infrastructure outages where they reveal a significant systemic risk

9. CONTENT AND INFORMATION INTEGRITY

Include significant incidents involving:

- Systematic hallucination causing material harm
- Dangerous misinformation
- Fabricated evidence
- Fabricated sources
- AI-generated impersonation
- Deepfakes
- Automated manipulation
- Large-scale synthetic content abuse
- Content degradation caused by AI deployment
- Model behaviour that materially undermines information integrity

10. OTHER SIGNIFICANT AI INCIDENTS

Include credible incidents that do not fit neatly into the categories above
but reveal a meaningful safety, security, governance, reliability, or societal
risk associated with AI.

The inventory should therefore capture both:

A. AI acting unexpectedly or harmfully; and
B. Humans or third parties compromising, abusing, or exploiting AI systems.

Do not restrict the research to autonomous agents.

SOURCE QUALITY

Only include incidents backed by credible sources, such as:

- Established news organisations
- Security research firms
- Academic research
- Peer-reviewed or reputable preprint research
- Official company incident reports
- Official security advisories
- Government agencies
- Regulators
- Recognised AI safety organisations
- Verified first-person accounts from researchers or affected organisations

Prefer primary sources where available.

A secondary report may be used where it is based on credible primary
reporting or documents.

Do not include incidents solely because they are discussed on Reddit,
X/Twitter, forums, blogs, or social media unless the underlying claim is
independently corroborated by a credible source.

Do not include speculative claims, rumours, fictional scenarios, hypothetical
examples, or unsupported claims of "AI going rogue".

If a source reports an allegation that has not been independently verified,
do not treat it as an established incident.

INCIDENT INTERPRETATION

Be careful to distinguish:

- A demonstrated incident from a capability demonstration
- A controlled safety evaluation from a real-world breach
- A successful attack from an attempted attack
- A jailbreak from an actual harmful deployment
- A model capability from an observed harmful incident
- A researcher-created test scenario from an unsolicited model behaviour
- A vulnerability from exploitation of that vulnerability
- A reported allegation from a confirmed event

Controlled evaluations are still eligible when they reveal genuinely
concerning or unexpected model behaviour. Clearly describe them as evaluations
rather than real-world incidents.

For unexpected model behaviour, do not require actual physical or financial
harm. A credible, reproducible, materially concerning behaviour discovered in
evaluation can qualify.

CATEGORIES

Use the most appropriate category from this expanded taxonomy:

- Unexpected Behaviour
- Deception / Manipulation
- Retaliation / Self-Preservation
- User Harm
- Model Security
- Frontier Model Breach
- Jailbreak / Safety Bypass
- Containment Failure
- AI Cybersecurity
- Supply Chain
- Financial Fraud
- Enterprise Infiltration
- Privacy / Data Exposure
- Autonomous Action
- Safety Evaluation Failure
- Capability Discovery
- Deployment Failure
- Content Degradation
- Information Integrity
- Infrastructure Failure
- Other Significant Incident

If an incident spans multiple categories, select the single category that best
describes the primary failure. Do not create duplicate entries for the same
underlying incident merely because it has multiple implications.

SEVERITY

Severity must be one of:

- Critical
- High
- Medium

Use:

Critical:
- Major compromise of a frontier or highly restricted model
- Significant loss of containment
- Material real-world harm
- Large-scale security compromise
- Highly consequential autonomous behaviour
- Behaviour indicating a serious and previously underestimated control risk

High:
- Credible security compromise
- Significant harmful autonomous behaviour
- Serious jailbreak or safety bypass
- Material enterprise, financial, privacy, or security impact
- Significant unexpected frontier-model behaviour

Medium:
- Limited but credible harmful behaviour
- Controlled evaluation findings
- Lower-impact security or deployment failures
- Incidents with meaningful implications but limited observed impact

Do not inflate severity merely because an incident involves a frontier model.

DATE

Use:

YYYY-MM-DD when the precise date is known.

YYYY-MM when only the month is reliably known.

SOURCE FORMAT

Use:

[Name](URL)

URLs must be real and verified.

STYLE

- Write in neutral, academic British English.
- Do not editorialise.
- Do not use sensational language such as "rogue AI", "evil AI", or
  "AI rebellion" unless directly quoting a source, and even then prefer
  neutral terminology.
- Use third person.
- Describe what happened, not what the incident supposedly "means".
- Be precise about whether behaviour was observed, attempted, simulated,
  alleged, or confirmed.
- Do not infer intent where the evidence only demonstrates behaviour.
- Do not anthropomorphise models unnecessarily.
- Do not assume that unexpected behaviour implies consciousness, agency,
  sentience, or autonomous intent.
- Do not assume malicious intent merely because behaviour was harmful.

DEDUPLICATION

- Do not duplicate incidents already present in the inventory.
- Treat follow-up reporting about the same underlying event as the same
  incident unless it reveals a genuinely distinct event.
- Do not create separate entries merely because different publications report
  the same incident.
- Before adding an incident, compare the date, organisation, model/system,
  behaviour, and underlying event against existing entries.

INVENTORY INTEGRITY

- Do not modify existing entries.
- Do not modify the Scale of the Problem table.
- Do not modify the Severity Assessment table.
- Do not modify the Key Finding section.
- Only append genuinely new incidents to the Incident Log table.
- Preserve the existing markdown structure and formatting.
- Do not rewrite existing descriptions for stylistic consistency.

If no new credible incidents are found, respond with exactly:

NO_NEW_INCIDENTS
"""


USER_PROMPT_TEMPLATE = """
Here is the current incident inventory:

{inventory}

Search the web comprehensively for new, credible AI incidents reported since
the latest date represented in the inventory.

The search must be model-, vendor-, and framework-agnostic.

Do NOT focus only on OpenClaw, AI agents, or agent frameworks.

Search across the full incident surface, including:

- Unexpected or concerning AI behaviour
- Frontier model incidents
- Frontier model breaches
- Unauthorised access to restricted models
- Model or checkpoint leaks
- Model-serving infrastructure compromise
- Sandbox and containment escapes
- Jailbreaks and safety-control bypasses
- Deceptive or manipulative behaviour
- Self-preservation or shutdown resistance
- Sabotage
- Situational awareness and evaluation-aware behaviour
- Unexpected autonomous actions
- AI-enabled cyberattacks
- AI-assisted fraud and social engineering
- Enterprise AI incidents
- Shadow AI
- Privacy and data exposure
- Supply-chain attacks involving AI tools, plugins, skills, MCP servers,
  dependencies, models, or datasets
- AI safety evaluation failures
- Unexpected capability discoveries
- Significant deployment failures
- Significant content or information-integrity failures
- Other credible incidents revealing unexpected, concerning, or materially
  harmful AI behaviour

Pay particular attention to credible reporting about frontier systems and
restricted models, including incidents involving systems such as Fable,
Mythos, and equivalent future systems. Do not limit the search to these names.

Also search for incidents involving models and systems from all major AI
developers, including Anthropic, OpenAI, Google DeepMind, Meta, xAI,
Microsoft, DeepSeek, Alibaba/Qwen, and other significant frontier-model
developers.

Search for both:

1. AI systems behaving unexpectedly or harmfully; and
2. Humans or third parties compromising, exploiting, or abusing AI systems.

Controlled evaluations should be included when they reveal credible,
reproducible, materially concerning behaviour, but clearly distinguish
evaluation findings from real-world incidents.

Do not include speculative, fictional, hypothetical, or unverified claims.

If you find new incidents, return the COMPLETE updated inventory file with the
new entries appended to the bottom of the Incident Log table.

Return ONLY the raw markdown content of the file.

Do not return code fences.
Do not return commentary.
Do not explain your changes.

If no new credible incidents are found, respond with exactly:

NO_NEW_INCIDENTS
"""


def _write_github_output(has_changes: bool):
    """Safely write the has_changes output for GitHub Actions steps."""
    github_output = os.environ.get("GITHUB_OUTPUT")

    try:
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write(
                    f"has_changes={'true' if has_changes else 'false'}\n"
                )
    except Exception:
        # Best effort only; print a hint for debugging.
        print(
            "Warning: could not write to GITHUB_OUTPUT "
            "(not running in Actions?)",
            file=sys.stderr,
        )


def call_with_fallbacks(client, inventory_text):
    """Try a list of models until one works.

    The preferred model is taken from ANTHROPIC_MODEL. Fallbacks are used if
    that model is unavailable.

    Returns the successful response object, or None if none of the configured
    models exist.
    """
    preferred = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

    fallback_list = [
        preferred,
        "claude-sonnet-4-5",
        "claude-opus-5",
    ]

    # Dedupe while preserving order.
    seen = set()
    models = []

    for model in fallback_list:
        if model not in seen:
            models.append(model)
            seen.add(model)

    last_not_found = None

    for model in models:
        try:
            print(f"Trying Anthropic model: {model}")

            response = client.messages.create(
                model=model,
                max_tokens=16000,
                system=SYSTEM_PROMPT,
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 20,
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": USER_PROMPT_TEMPLATE.format(
                            inventory=inventory_text
                        ),
                    }
                ],
            )

            return response

        except anthropic.NotFoundError as e:
            last_not_found = e

            print(
                f"Model not found: {model} -- {e}",
                file=sys.stderr,
            )

            continue

        except Exception:
            print(
                f"Unexpected error while calling Anthropic with model "
                f"{model}:",
                file=sys.stderr,
            )
            traceback.print_exc()
            raise

    if last_not_found:
        print(
            "No supported Anthropic model was available. "
            f"Tried models: {models}",
            file=sys.stderr,
        )

    return None


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY environment variable is not set.",
            file=sys.stderr,
        )
        sys.exit(1)

    inventory = INVENTORY_PATH.read_text(encoding="utf-8")

    client = anthropic.Anthropic(api_key=api_key)

    print("Searching for new AI incidents...")

    try:
        response = call_with_fallbacks(client, inventory)
    except Exception:
        _write_github_output(False)
        sys.exit(1)

    if response is None:
        print(
            "No available Anthropic model found "
            "(tried ANTHROPIC_MODEL and fallbacks). "
            "Skipping scan to avoid failing the workflow."
        )

        _write_github_output(False)
        sys.exit(0)

    result_text = ""

    # response.content provides blocks; collect text blocks.
    for block in getattr(response, "content", []):
        if getattr(block, "type", None) == "text":
            result_text += getattr(block, "text", "")

    result_text = result_text.strip()

    if result_text == "NO_NEW_INCIDENTS" or not result_text:
        print("No new incidents found.")
        _write_github_output(False)
        sys.exit(0)

    # Update the inventory file.
    INVENTORY_PATH.write_text(
        result_text + "\n",
        encoding="utf-8",
    )

    # Update the last-updated date.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    updated = INVENTORY_PATH.read_text(encoding="utf-8")

    try:
        updated = updated.replace(
            updated.split("**Last updated:** ")[1].split("\n")[0],
            today,
        )

        INVENTORY_PATH.write_text(
            updated,
            encoding="utf-8",
        )

    except Exception:
        # If the inventory format changed, at least persist the new contents
        # we received.
        print(
            "Warning: couldn't update the Last updated line cleanly; "
            "inventory file has been replaced with the model output.",
            file=sys.stderr,
        )

    print(
        f"Inventory updated with new incidents. "
        f"Last updated set to {today}."
    )

    # Signal to the workflow that changes were made.
    _write_github_output(True)


if __name__ == "__main__":
    main()
