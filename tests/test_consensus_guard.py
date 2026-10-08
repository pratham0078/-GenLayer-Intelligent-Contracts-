from contracts.consensus_guard import equivalent, normalize_result


def test_normalize_result_accepts_valid_result():
    result = normalize_result(
        {
            "decision": "approve",
            "score": 90,
            "evidence": "The source directly supports the claim.",
            "rationale": "The published source contains the relevant evidence.",
        }
    )

    assert result["decision"] == "approve"
    assert result["score"] == 90


def test_equivalent_accepts_close_consensus():
    leader = {
        "decision": "approve",
        "score": 90,
        "evidence": "The source supports the claim.",
        "rationale": "The evidence is directly relevant.",
    }

    validator = {
        "decision": "approve",
        "score": 82,
        "evidence": "The source also supports the claim.",
        "rationale": "The evidence is consistent.",
    }

    assert equivalent(leader, validator) is True


def test_equivalent_rejects_different_decision():
    leader = {
        "decision": "approve",
        "score": 90,
        "evidence": "The source supports the claim.",
        "rationale": "The evidence is directly relevant.",
    }

    validator = {
        "decision": "reject",
        "score": 90,
        "evidence": "The source contradicts the claim.",
        "rationale": "The evidence points in the opposite direction.",
    }

    assert equivalent(leader, validator) is False


def test_equivalent_rejects_large_score_difference():
    leader = {
        "decision": "approve",
        "score": 95,
        "evidence": "The source supports the claim.",
        "rationale": "The evidence is directly relevant.",
    }

    validator = {
        "decision": "approve",
        "score": 60,
        "evidence": "The source supports the claim.",
        "rationale": "The evidence is somewhat relevant.",
    }

    assert equivalent(leader, validator) is False
