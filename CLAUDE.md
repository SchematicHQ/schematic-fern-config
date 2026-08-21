# schematic-fern-config

Fern docs config and MDX source for docs.schematichq.com.

Read `.claude/docs-conventions.md` before adding a page, adding a hub, or changing navigation.
It covers the `npx fern-api check` gotcha, why a page's URL never follows its directory, and
which SDK pages are generated and will be overwritten.

## Writing rules

These apply to every `.mdx` file under `fern/docs/pages/`. Nothing blocks a merge on them.
`scripts/prose_lint.py` covers the mechanical ones and runs weekly to catch drift, so follow the
rules as you write rather than expecting a gate to catch you. Run it locally before opening a PR.

**No em dashes in body prose.** Use commas or periods, or restructure. The one exception is the
hub-bullet format, `- [Link](/slug) — lowercase outcome sentence`, which is a sanctioned
convention.

**No short declarative sentences that only restate the sentence before them.**

**Put a person in the subject slot.** When a sentence is hard to follow, the cause is usually a
grammatical subject that is an abstraction, leaving the reader to reconstruct who does what.
"The problem this solves is", "Assembling that by hand means", and "Checking by hand means" all
bury the actor in a gerund or an object. Name the reader or the role and make them the subject.

**One tense per sentence, and prefer the present.** Stacking a present verb, an infinitive, a
gerund, and a past participle into one sentence makes the reader hold three time frames at once.
"has been using" is the heaviest construction available and almost never earns its place.

**State the point instead of framing it.** "The problem this solves is X" and "The last one
matters more than it looks" announce that a point is coming rather than making it. Cut the
announcement.

**Give the reader verbs, not a pile of nouns.** "means the plan, the entitlements attached to it,
and usage against each metered feature" hands over three nouns and leaves the reader to work out
what to do with them.

**Document what the product does, not what it lacks.** Never open a section by cataloging an
absent capability, and never present a workaround as compensation for a gap. "Enforcement
operates on entitlements and on the company balance, not on per-actor caps. No field limits how
much of a company's balance an individual user or agent may consume" tells the reader about a
hole in the product they had not asked about. Describe the mechanism that exists and let the
reader decide whether it covers them.

The test: if a sentence would be deleted the day a feature ships, it is a roadmap note and does
not belong in the docs. Phrases like "does not yet", "not currently supported", and "the caps
that don't ship" fail it.

A constraint on something you are actively describing is different and is welcome, because it
changes what the reader builds. "This call is non-blocking and there is no response to check"
and "A billing entity can only be set when a subscription is started" both stop a real mistake
and stay true after the next release.

**Every setup paragraph needs a consequence.** A paragraph introducing a list or an example has
to earn it, and accurately describing a chore is not a point. Say what the chore costs, so what
follows reads as the answer to something.

Description, not a point: `Each one is a separate lookup, and the call comes back every quarter.`
A point: `Each one is a separate lookup, so plenty of CSMs skip it and walk into the call
guessing.`

## Verifying

```sh
npx fern-api check          # not `npx fern check`, see docs-conventions.md
python3 scripts/prose_lint.py
```
