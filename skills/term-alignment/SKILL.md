---
name: term-alignment
description: "Review project terminology: unclear jargon, competing names for the same concept, and names for related concepts. Let the user choose names and definitions in a worksheet before applying changes across code and documentation. Use when asked to align, define, review, or rename project terminology or jargon."
disable-model-invocation: true
---

# Term Alignment

Make the project's vocabulary legible: define jargon, consolidate competing names for the same concept, and choose clear names.

## Scope

Review the code and documentation the user names. If they name nothing, review the whole repository. Skip standard terminology unless its local meaning is surprising or overloaded.

## Workflow

1. **Find naming decisions:** terms that are obscure, misleading, or unnecessarily bespoke; different terms that may name the same concept; and related concepts whose relationship is unclear. Check actual usage before calling terms synonyms, and say when usage doesn't settle it.

2. **Write a worksheet** as a Markdown file outside the repository and give the user its path. Use one numbered entry per decision:

   ```markdown
   ## 3. Existing: `job_lease`, `claim`
   **Used in:** `src/queue.py:40` (`job_lease`), `docs/workers.md` (claim)
   **Meaning:** Both mark a job as taken by one worker until a timeout, so they're the same concept. (Inferred from usage.)
   **Proposed:** `claim` everywhere, because it matches the CLI verb. Alternative: `lock`.
   **Affects:** internal identifiers, prose
   **Decision:**
   ```

   For related but distinct concepts, explain how they relate. Propose an umbrella name only if it helps understanding, and give each independently choosable name its own `Decision:` line. When a term is clear enough but never explained, offer keeping it and defining it where readers first meet it as an option.

3. **Wait** for the user to edit the worksheet. Don't change anything before they reply.

4. **Apply** the decisions consistently within the chosen scope: rename identifiers, comments, prose, and file names, and add the definitions the user chose. Leave blank decisions unchanged. A shared name doesn't authorize merging implementations, and an umbrella term doesn't authorize a new abstraction. Ask before applying any decision that is ambiguous, would erase a real distinction, or needs structural changes. Run the project's checks, then summarize what changed.
