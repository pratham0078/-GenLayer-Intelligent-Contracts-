# Consensus Guard for GenLayer

A reusable Intelligent Contract primitive for **validator-backed evidence verification**.

Consensus Guard lets an application submit:

- a natural-language claim
- a public HTTP(S) source

The contract then uses GenLayer's non-deterministic execution and Equivalence Principle to independently evaluate the source.

The important property is not that an LLM produces an answer. The important property is that **validators independently re-check the evidence and only accept the proposed result when the logical decision agrees**.

## Why this is useful

Many applications need to turn external information into an on-chain state transition:

- verify whether a public announcement supports a claim
- verify whether a policy condition is satisfied
- verify whether an external status has changed
- build agent permission or workflow gates
- create evidence-backed dispute or review systems

A conventional smart contract cannot directly interpret arbitrary web evidence. A single off-chain AI service creates a trust bottleneck.

Consensus Guard provides a reusable pattern:

```text
claim + source
      |
      v
 leader independently fetches + evaluates
      |
      v
 candidate result
      |
      v
 validators independently fetch + evaluate
      |
      v
 decision + confidence equivalence
      |
   +--+----------------+
   |                   |
 agree              disagree
   |                   |
   v                   v
state update       consensus rejects
```

## Consensus rule

The contract uses a custom `run_nondet_unsafe` leader/validator pair.

A validator does **not** merely check whether the leader returned valid JSON. It independently:

1. fetches the same source URL
2. evaluates the same claim
3. normalizes its own result
4. compares the logical decision
5. checks that confidence is within a 15-point tolerance
6. requires substantive evidence

The accepted result is then written to deterministic contract state.

### Equivalence

Two results are considered equivalent when:

- `decision` is identical
- confidence/score differs by no more than 15 points
- both results contain substantive evidence

Rationale text does not need to match because natural-language explanations are inherently non-deterministic.

## State design

The contract stores the latest accepted verification:

```text
request_id
claim
source_url
decision
score
evidence
rationale
total_resolved
```

The non-deterministic block never writes contract storage. Storage is updated only after the consensus operation returns to deterministic execution.

## Decisions

The verifier can return:

- `approve` — source materially supports the claim
- `reject` — source materially contradicts the claim
- `inconclusive` — source does not provide enough evidence

This makes uncertainty explicit instead of forcing every question into a binary answer.

## Security model

### Leader is not trusted

The validator independently evaluates the source. A leader cannot make an arbitrary result acceptable merely by returning correctly formatted JSON.

### Disagreement is meaningful

If validators disagree on the logical decision or confidence diverges beyond the tolerance, the validator rejects the leader result. GenLayer consensus can then handle the failed proposal according to the protocol.

### Deterministic state transition

Web access and LLM execution happen inside the non-deterministic block. Contract storage is updated only after the result passes GenLayer's consensus mechanism.

### Evidence is bounded

The source content sent to the evaluator is capped at 30,000 characters, and stored evidence/rationale are bounded before entering contract state.

## Example

A caller can submit:

```text
Claim:
"The organization announced that its mainnet launched."

Source:
https://example.org/announcement
```

The leader produces a structured result such as:

```json
{
  "decision": "approve",
  "score": 88,
  "evidence": "The announcement states that mainnet went live...",
  "rationale": "The source directly confirms the launch."
}
```

Validators independently perform the same evidence check.

If their decision agrees and their scores remain within the configured tolerance, the result becomes contract state.

## Repository structure

```text
.
├── contracts/
│   └── consensus_guard.py
├── tests/
│   └── test_consensus_guard.py
├── README.md
└── requirements-dev.txt
```

## Local deterministic tests

The included tests exercise the equivalence policy without requiring a live GenLayer network.

```bash
pip install -r requirements-dev.txt
pytest
```

## Deploying

The contract is written for the GenLayer Intelligent Contract environment.

Example CLI flow:

```bash
genlayer network set studio-dev
genlayer network info
genlayer deploy --contract contracts/consensus_guard.py
```

Use the current GenLayer documentation for the target network, SDK/CLI version, fees, and deployment requirements.

## Extending the primitive

Builders can reuse the consensus pattern while replacing the evaluator with their own domain logic.

Examples:

### Agent authorization

```text
agent request
    -> external policy
    -> independent validator evaluation
    -> approved / rejected
```

### Public announcement verification

```text
claim
    -> official source
    -> independent evidence checks
    -> verified / disputed
```

### Workflow gate

```text
condition
    -> external evidence
    -> validator consensus
    -> execute next state transition
```

### Dispute resolution

```text
claim + evidence
    -> independent evaluation
    -> approve / reject / inconclusive
```

## Design limitations

Consensus does not magically make external information truthful.

The source can be wrong, unavailable, manipulated, or incomplete. This primitive provides **consensus over a defined verification procedure**, not an absolute truth oracle.

The source URL is also part of the request. Applications that require stronger provenance should add domain allowlists, source snapshots, timestamps, multiple independent sources, or application-specific evidence rules.

## Why this is a GenLayer primitive

The reusable part of this project is the consensus boundary:

> **non-deterministic evidence evaluation → independent validator verification → explicit equivalence → deterministic state**

That pattern can be embedded into many Intelligent Contracts without requiring every builder to design the leader/validator flow from scratch.

## License

MIT
