EXTRACT_SYSTEM = "You extract factual claims from text. You output only valid JSON."

EXTRACT_PROMPT = """Extract up to {max_claims} factual claims from the answer below.
Only include claims that state a specific fact. Copy each claim's text EXACTLY as written in the answer.
Type each claim as one of: "pricing" (prices, plan costs, free-tier limits),
"api_version" (version numbers, deprecations, endpoint status), or "other".
For pricing and api_version claims, set "subject" to the product or API name.

Return ONLY a JSON array like:
[{{"text": "...", "type": "pricing", "subject": "Pro plan"}}]

Answer:
\"\"\"{answer}\"\"\"
"""

JUDGE_SYSTEM = "You check whether a claim matches current web sources. You output only JSON. Use only the sources provided."

JUDGE_PROMPT = """Claim: {claim}

Current sources:
{context}

Decide whether the sources confirm, contradict, or don't clearly address the claim.
- "confirmed": the sources clearly agree with the claim.
- "contradicted": the sources clearly show a different current value.
- "unclear": the sources are missing, conflicting, or don't address the claim.

Return ONLY JSON:
{{"verdict": "confirmed|contradicted|unclear", "current_value": "value from sources or null", "reason": "one sentence citing the source", "source_indices": [0]}}
"""

SUMMARY_PROMPT = """Given the original answer and the verified claims with their verdicts, write a brief, one-sentence summary sentence describing the overall freshness state (e.g., "2 of 3 checkable claims are out of date", or "All checkable claims are fully up to date").

If no checkable claims exist, say "No checkable claims found".

Claims:
{claims_json}

Return ONLY the summary sentence as plain text.
"""

REWRITE_PROMPT = """You are an expert technical editor. Rewrite the given AI answer so that all contradicted or outdated claims are corrected with their current verified values from the audit results. Keep the tone identical to the original answer.

Original Answer:
{answer}

Audit Results (Claims with Current Values):
{claims_json}

Return ONLY the fully corrected answer text, with no extra commentary or markdown fencing. Do not include any reasoning, labels, or analysis. Just the corrected text.
"""