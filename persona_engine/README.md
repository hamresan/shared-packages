# hamresan-persona-engine

Reusable persona initialization for account-authored text.

The package keeps persona separate from knowledge. Persona describes writing style only and must not
be used as a store of business facts, product facts, policies, prices, or other authoritative
knowledge.

## Public model

`PersonaProfile` contains measurable style characteristics:

- verbosity;
- sentence style;
- emoji usage;
- hashtag usage;
- exclamation usage;
- line-break style;
- generated style guidelines;
- source sample count.

## Baseline generator

The initial package includes a deterministic baseline generator. It extracts observable writing
patterns from representative account-authored text without calling an external model.

Applications depend on the `PersonaGenerator` contract, so a future LLM-backed generator can replace
the baseline without changing consuming application services.
