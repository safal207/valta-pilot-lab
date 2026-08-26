# PLC 1 — Accepted Is Not Settled

Target release: 2026-09-02  
Stage: Prelaunch Content 1 — Opportunity  
Primary format: short email with optional public post

## Subject

```text
Your payment API said “accepted.” Did the money move once?
```

## Email

Hi {{name/team}},

The most expensive payment failures rarely look like a clean `FAILED` response.

They look like this:

```text
payment authorized
-> request dispatched
-> provider received it
-> caller lost the response
-> automated retry started
```

At that point, both attempts can look locally reasonable.

The first system says, “I timed out.”  
The retry logic says, “No success was recorded.”  
The policy engine says, “The action is still allowed.”

But none of those statements answers the financial question:

> Did zero, one, or two economic effects actually occur?

This gap matters more as payment workflows become agentic. An AI agent can follow policy perfectly and still make the wrong recovery decision if the effect of the previous attempt is unknown.

A useful control model separates five facts:

```text
1. Was the exact action authorized?
2. Did one execution attempt durably own the dispatch boundary?
3. What did the provider or transport report?
4. What economic effect was independently observed?
5. Is the correct next action finalize, stop, or reconcile?
```

Here is a seven-question self-test for any automated payment, payout, or settlement flow:

1. Is authorization bound to the exact amount, target, action, and policy version?
2. Is ownership of execution durably reserved before dispatch?
3. Can an old process be fenced after a restart or retry?
4. Is provider acceptance kept separate from final settlement?
5. Can the final economic effect be observed independently of the caller’s own claim?
6. Does an unknown outcome block blind retry?
7. Can another party replay the evidence and reach the same verdict?

A “no” is useful. It identifies the exact boundary where automation still depends on hope or manual reconciliation.

**Which one step in your current flow is still unknown, inferred, or manually reconciled?**

Alexey Safonov

## Public post version

### Your payment API said “accepted.” Did the money move exactly once?

The dangerous payment state is often not `FAILED`.

It is:

```text
authorized
-> dispatched
-> response lost
-> retry started
```

An authorization log proves permission.  
An API response proves what one service reported.  
A retry record proves another attempt happened.

None of those facts alone proves the final economic outcome.

For automated and AI-driven payments, the minimum useful model is:

```text
exact authorization
-> durable execution ownership
-> dispatch evidence
-> independent effect observation
-> finalize or reconcile
```

Seven questions worth asking:

1. Is authorization bound to the exact action?
2. Is execution reserved before dispatch?
3. Can stale workers be fenced?
4. Is acceptance separate from settlement?
5. Is the effect independently observable?
6. Does uncertainty block blind retry?
7. Can the verdict be replayed from evidence?

The opportunity is not to promise that uncertainty disappears.

It is to make uncertainty explicit before it becomes a duplicate payment, false success, or expensive incident.

## CTA handling

If the reader replies with a boundary:

```text
Thanks — that is a useful boundary.

What are the two hardest questions your team has about it: one technical and one operational/economic?

I have an executable recovery model for this class of failure. I am collecting the real questions first so the next material addresses the problem teams actually have.
```

Do not mention price or ask for a meeting in the first PLC response.
