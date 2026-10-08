# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


ALLOWED_DECISIONS = ("approve", "reject", "inconclusive")


def normalize_result(raw) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("validator response must be a JSON object")

    decision = str(raw.get("decision", "")).strip().lower()

    if decision not in ALLOWED_DECISIONS:
        raise ValueError("invalid decision")

    score = raw.get("score", -1)

    try:
        score = int(score)
    except (TypeError, ValueError):
        raise ValueError("score must be an integer")

    if score < 0 or score > 100:
        raise ValueError("score must be between 0 and 100")

    evidence = str(raw.get("evidence", "")).strip()
    rationale = str(raw.get("rationale", "")).strip()

    if len(evidence) < 10:
        raise ValueError("evidence is required")

    if len(rationale) < 10:
        raise ValueError("rationale is required")

    return {
        "decision": decision,
        "score": score,
        "evidence": evidence[:500],
        "rationale": rationale[:1000],
    }


def build_prompt(claim: str, source_url: str, source_text: str) -> str:
    return f"""
You are an independent evidence verifier.

CLAIM:
{claim}

SOURCE URL:
{source_url}

SOURCE CONTENT:
{source_text}

Return ONLY a JSON object with these fields:
{{
  "decision": "approve" | "reject" | "inconclusive",
  "score": 0-100,
  "evidence": "short factual evidence from the source",
  "rationale": "short explanation"
}}

Rules:
- approve only when the source materially supports the claim
- reject when the source materially contradicts the claim
- inconclusive when the source does not provide enough evidence
- never invent evidence
- score is confidence in your evaluation, not probability of truth
""".strip()


def evaluate(claim: str, source_url: str) -> dict:
    page = gl.nondet.web.get(source_url)
    source_text = page.body.decode("utf-8", errors="ignore")[:30000]

    prompt = build_prompt(claim, source_url, source_text)
    raw = gl.nondet.exec_prompt(prompt, response_format="json")

    return normalize_result(raw)


def equivalent(leader_result: dict, validator_result: dict) -> bool:
    if leader_result["decision"] != validator_result["decision"]:
        return False

    if abs(leader_result["score"] - validator_result["score"]) > 15:
        return False

    if len(leader_result["evidence"]) < 10:
        return False

    if len(validator_result["evidence"]) < 10:
        return False

    return True


class ConsensusGuard(gl.Contract):
    last_request_id: u32
    total_resolved: u32
    last_claim: str
    last_source_url: str
    last_decision: str
    last_score: u32
    last_evidence: str
    last_rationale: str

    def __init__(self):
        self.last_request_id = 0
        self.total_resolved = 0
        self.last_claim = ""
        self.last_source_url = ""
        self.last_decision = "inconclusive"
        self.last_score = 0
        self.last_evidence = ""
        self.last_rationale = ""

    @gl.public.write
    def verify(self, claim: str, source_url: str) -> str:
        if not claim or len(claim) > 1000:
            raise gl.UserError("claim must contain 1-1000 characters")

        if not source_url.startswith(("http://", "https://")):
            raise gl.UserError("source_url must be an HTTP(S) URL")

        def leader_fn():
            return evaluate(claim, source_url)

        def validator_fn(leader_result):
            try:
                if not isinstance(leader_result, gl.vm.Return):
                    return False

                leader_data = leader_result.calldata
                validator_data = evaluate(claim, source_url)

                return equivalent(leader_data, validator_data)

            except Exception:
                return False

        result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn
        )

        self.last_request_id += 1
        self.total_resolved += 1
        self.last_claim = claim
        self.last_source_url = source_url
        self.last_decision = result["decision"]
        self.last_score = result["score"]
        self.last_evidence = result["evidence"]
        self.last_rationale = result["rationale"]

        return json.dumps(result, sort_keys=True)

    @gl.public.view
    def get_last_result(self) -> str:
        return json.dumps(
            {
                "request_id": self.last_request_id,
                "claim": self.last_claim,
                "source_url": self.last_source_url,
                "decision": self.last_decision,
                "score": self.last_score,
                "evidence": self.last_evidence,
                "rationale": self.last_rationale,
                "total_resolved": self.total_resolved,
            },
            sort_keys=True,
        )
