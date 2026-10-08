# GenLayer Consensus Guard

A reusable GenLayer Intelligent Contract primitive for validator-backed evidence verification.

## Overview

Consensus Guard lets an application submit:

- a natural-language claim
- a public HTTP(S) source

The contract uses GenLayer's non-deterministic execution and validator consensus to independently evaluate the source.

The key idea is simple:

> A single AI response should not automatically become the source of truth for an on-chain state transition.

Consensus Guard creates an explicit leader/validator verification boundary.

## Live Deployment

The contract has been deployed on GenLayer Studio.

Contract address:

`0xc3D340E266f061f84573f407fcBC57C86267271d`

GenLayer Explorer:

https://explorer-studio.genlayer.com/address/0xc3D340E266f061f84573f407fcBC57C86267271d

Deployment status:

`ACCEPTED`

## How Consensus Works

```text
Claim + Source
      |
      v
Leader evaluation
      |
      v
Proposed result
      |
      v
Independent validator evaluation
      |
      v
Equivalence check
      |
   +--+-----------+
   |              |
 AGREE        DISAGREE
   |              |
   v              v
State update   Rejected
