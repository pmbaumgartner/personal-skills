---
name: term-alignment
description: "Review project terminology: unclear jargon, competing names for the same concept, one name used for different concepts, and names for related concepts. Let the user choose names and definitions in a worksheet before applying changes across code, documentation, and the project's glossary if it has one. Use when asked to align, define, review, or rename project terminology or jargon, in a repository or on a branch."
disable-model-invocation: true
---

# Term Alignment

Make the project's vocabulary legible: define jargon, consolidate competing names for the same concept, separate concepts that share a name, and choose clear names.

## Scope

In a git repository, review the git-tracked files (`git ls-files`), narrowed to any paths the user names; ignored and untracked files, such as old plans and notes, are out of scope. Outside a repository, or when the user explicitly asks for untracked or ignored files, review the files and folders the user points to. Skip standard terminology unless its local meaning is surprising or overloaded.

When the user asks to review a branch, review the files it changes (`git diff --name-only <base>...HEAD`, with the base the user names or the default branch) and look only at terms the branch introduces or changes. The base branch's vocabulary is the reference: report branch terms that clash with it, and leave naming problems the branch didn't introduce alone.

## Glossary

Before scanning, look for the project's glossary: a `GLOSSARY.md`, or a terminology document or section the project already keeps. If there is one, it is the authority. Usage that contradicts it is drift: pre-fill the glossary's term and say so under **Meaning:**. Treat a glossary term as an open decision only when the glossary doesn't settle it or the user asks to revisit it.

If there is no glossary, don't create one unless the user chooses to in the worksheet.

## Workflow

1. **Find naming decisions:** terms that are obscure, misleading, or unnecessarily bespoke; different terms that may name the same concept; one term used for different concepts; and related concepts whose relationship is unclear. Check actual usage before calling terms synonyms or a term overloaded. When documentation describes a term in a way the code contradicts, say so and base the proposed definition on the code; changing behavior is out of scope.

2. **Write a worksheet** as a Markdown file in the current working directory and give the user its path. Use one numbered entry per decision:

   ```markdown
   ## 3. Existing: `job_lease`, `claim`
   **Used in:** `src/queue.py:40` (`job_lease`), `docs/workers.md` (claim)
   **Meaning:** Both mark a job as taken by one worker until a timeout. Usage doesn't show whether a lease can outlive its claim.
   **Test:** A worker's claim expires and another worker takes the job. Does the first worker still hold a `job_lease`? If not, they're the same concept.
   **Proposed:** `claim` everywhere, because it matches the CLI verb. Alternative: `lock`.
   **Affects:** internal identifiers, prose
   **Decision:** proposed 'claim'
   ```

   Add a **Test:** line only when usage doesn't settle whether terms name the same concept: a concrete scenario whose answer does. The user can answer it in the worksheet.

   For related but distinct concepts, explain how they relate. Propose an umbrella name only if it helps understanding. For one term used for different concepts, propose a name for each. Give each independently choosable name its own `Decision:` line. When a term is clear enough but never explained, offer keeping it and defining it as an option.

   Pre-fill each `Decision:` with your recommendation, using one of these values: `proposed 'name'` (apply the Proposed change), `alternative 'name'` (apply that alternative), `keep` (keep the existing term, adding a definition if one was offered), or `skip` (change nothing). Always put the name in single quotes after `proposed` or `alternative`. Tell the user they can overwrite any value with another one, or with their own name in single quotes.

   If the project has no glossary, end the worksheet with this entry, and tell the user that `yes` records the decided terms in a new `GLOSSARY.md`:

   ```markdown
   ## 9. Record these decisions in a new `GLOSSARY.md`?
   **Decision:** skip
   ```

3. **Wait** for the user to edit the worksheet. Don't change anything before they reply.

4. **Apply** the decisions consistently within the chosen scope: rename identifiers, comments, prose, and file names, and add the definitions the user chose. Treat the reply as confirming every decision as it now reads, including pre-filled ones the user left alone; `skip` or a blank decision changes nothing. A shared name doesn't authorize merging implementations, and an umbrella term doesn't authorize a new abstraction. Ask before applying any decision that is ambiguous, would erase a real distinction, or needs structural changes.

   With a glossary, existing or newly chosen, put definitions there instead of in prose, and update it for every decided term specific to the project, following its existing format. In a new `GLOSSARY.md`, give each term in bold followed by one or two sentences saying what it is. Leave out implementation details and general programming concepts. Without a glossary, define terms where readers first meet them.

   Run the project's checks, then summarize what changed. If the project has a glossary that its agent instructions (such as `AGENTS.md` or `CLAUDE.md`) don't mention, suggest adding a line telling agents to use its terms and to flag conflicts with it.
