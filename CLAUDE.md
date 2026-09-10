# board-gamez

`ARCHITECTURE.md` defines the layers and maps every path to one. Read it before
adding code.

Skills are loaded before the work they govern, not after:

- `.claude/skills/backend-development/` — before adding or changing any component
- `.claude/skills/python-style/` — before writing or editing any `.py`
- `.claude/skills/modeling/` — before writing or changing any `.proto`

## Write in plain language

This applies to code comments, documentation, commit messages and replies.

- State facts in declarative sentences. Do not build to a conclusion.
- Use few adjectives, and none that only add emphasis.
- Do not use rhetorical constructions: no "not X, but Y", no repetition for
  effect, no sentence whose purpose is to sound conclusive.
- Prefer the precise term to the vivid one. "Refuses a write built on an earlier
  version" rather than "guards against stale writes".
- A sentence that would be weaker as a plain statement of fact is doing something
  other than informing. Remove it.

## Comments are a source of truth, never a conversation

A comment states what is true of the thing it sits on. It never carries the
conversation that produced it. Someone reads it years later with no memory of
the discussion, no access to the alternatives, and no interest in them.

**Never write:**

- **Conversation context.** "for the reason given on X", "worth naming here",
  "this is the reason `dto/` exists", "as decided". If a comment only makes
  sense to someone who followed the argument, it is not documentation.
- **A comparison against code that is not there.** "composed rather than
  flattened", "named fields rather than a pair", "a cursor rather than an
  offset", "its own type rather than a shared one". The reader cannot see the
  alternative, cannot check the claim, and is left wondering what they missed.
- **The name of an implementation the contract does not bind to.** A model does
  not know who stores it, who sends it, or what it is written to. Never "as
  Redis holds it", never "one GET and one guarded SET" — a schema outlives every
  store behind it, and naming one turns a contract into a deployment note. If a
  type genuinely is a cache, that belongs in its **name**: `CachedTable`.
- **Meta-commentary about the layout.** Which directory a type lives in, and why,
  is a rule in the skill that governs the work. It is never the type's own
  comment.

**Write instead:**

- What the thing is, in a line.
- The constraint a reader would otherwise get wrong: that `captured_square`
  differs from `destination` for en passant, that `position_keys` runs one ahead
  of `turns`, that a timestamp is emission and not receipt.
- What a caller is obliged to do: send back the version you read.

The reasoning still matters — it just belongs in the reply to the person who
asked, not in the file. A rule that outlives one conversation belongs in the
skill that governs the work, where it is loaded before the next change is made.

**Prose beside code goes stale.** A README in a source directory is read once,
by whoever wrote it. Reach for a better name before reaching for an explanation.
