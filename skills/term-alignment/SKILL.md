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

Before scanning, look for the project's glossary: a `GLOSSARY.md`, or a terminology document or section the project already keeps. If there is one, it is the authority. Usage that contradicts it is drift: recommend the glossary's term and give the glossary as the reason. Treat a glossary term as an open decision only when the glossary doesn't settle it or the user asks to revisit it.

If there is no glossary, don't create one unless the user chooses to in the worksheet.

## Workflow

1. **Find naming decisions:** terms that are obscure, misleading, or unnecessarily bespoke; different terms that may name the same concept; one term used for different concepts; and related concepts whose relationship is unclear. Check actual usage before calling terms synonyms or a term overloaded.

   Documentation and code sometimes disagree. When a term can't be defined without picking a side, that is a decision for the user: recommend the meaning the code supports and say what the documentation claims. Any other mismatch you happen to notice, such as documentation describing behavior the code doesn't have, is not a naming decision: give it one line under **Noticed while reading** in the worksheet and change nothing for it. That list is a courtesy, not an audit, so don't go looking for mismatches or test the code to confirm them. Changing behavior is out of scope.

2. **Write a worksheet** as a Markdown file in a temporary directory, named for the project (such as `term-alignment-queue-service.md`). Outside the repository it can't be committed by accident or turn up in searches, and it needs no cleanup. Sort the decisions into two sections, so the user reads closely only where their judgment is needed:

   - **Needs your call:** usage doesn't settle whether terms name the same concept, documentation and code disagree about what a term means, the choice between names is close, or the recommendation would change a public name (one that users, other programs, or stored data depend on, such as a CLI flag, config key, API field, or database column).
   - **Routine:** every other decision.

   ```markdown
   # Term alignment: 3 decisions

   Applying this worksheet as checked changes no public names. Paths are relative to `/Users/sam/src/queue-service`.

   Each decision is pre-checked with the recommendation. To choose differently, move the `x` or write your own after `Other:`. Uncheck everything in a group to change nothing.

   ## Needs your call (1)

   ### 1. `job_lease` and `claim`: one concept or two?

   Both mark a job as taken by one worker until a timeout. Usage doesn't show whether a lease can outlive its claim.

   - `job_lease` (12 uses, 3 files): `job_lease = store.acquire(job_id, ttl=30)` in `src/queue.py:40`
   - claim (5 uses, 2 files): "A worker claims a job before running it." in `docs/workers.md:12`

   **Question:** A worker's claim expires and another worker takes the job. Does the first worker still hold a `job_lease`? If not, they're the same concept.

   **Your answer (optional):**

   - [x] `claim` everywhere: it matches the CLI verb (recommended)
   - [ ] `lock` everywhere: also renames the `claim` CLI command
   - [ ] Keep both and define each
   - [ ] Other:

   ## Routine (2)

   Uncheck a line to skip it, or rewrite it to choose something else.

   - [x] 2. `ws`, `work_dir` → `workspace`. One directory, three names. 23 uses, 6 files.
   - [x] 3. Keep `tombstone` and define it. It is used 9 times and never explained.

   ## Noticed while reading

   These aren't naming decisions, and nothing here will be changed.

   - `docs/workers.md:30` says a claim times out after 60 seconds, but `src/queue.py:12` sets 30.
   ```

   Open with the number of decisions, whether applying the worksheet as checked would change any public names, and the project root that the worksheet's paths are relative to. Number the entries in worksheet order, and leave out a section that has nothing in it.

   In a **Needs your call** entry:

   - Ask the question in the heading.
   - Say what the terms mean in a sentence or two. For related but distinct concepts, explain how they relate.
   - Give each term, or each meaning of a shared term, one bullet with its use and file counts and one short real line that shows what it means, quoted exactly, with its location. Get counts from a search rather than guessing; they show how big a change is, so they needn't be exact.
   - Add **Question:** and **Your answer (optional):** only when usage doesn't settle whether terms name the same concept. The question is a concrete scenario whose answer does. Recommend an option that can be applied as it stands, because the user may leave the answer blank.
   - List the options as checkboxes, each with its reason in a few words, ending with `Other:`. Check the one you recommend and mark it `(recommended)`. Say when an option would change a public name, and what the new name would be. Propose an umbrella name only if it helps understanding. When a term is clear enough but never explained, offer keeping it and defining it.
   - Keep each checkbox group to one choice. When an entry holds more than one, such as a name for each concept that shares a term, or whether a public name should follow a rename, give each choice its own labelled group, and say so when one only makes sense given another.

   A **Routine** entry is one checked line: its number, the change, the reason in one sentence, and for a rename how many uses and files it changes.

   If the project has no glossary, add this section after the routine entries:

   ```markdown
   ## Glossary

   - [ ] Record these decisions in a new `GLOSSARY.md`
   ```

   Give the user the worksheet's full path and say how many decisions need their call.

3. **Wait** for the user to edit the worksheet. Don't change anything before they reply.

4. **Apply** the decisions consistently within the chosen scope: rename identifiers, comments, prose, and file names, and add the definitions the user chose. Treat the reply as confirming every decision as it now reads, including pre-checked ones the user left alone. Text after `Other:` is the user's choice even if another box is still checked. A group or routine line with nothing checked changes nothing. A shared name doesn't authorize merging implementations, and an umbrella term doesn't authorize a new abstraction. Ask before applying any decision that is ambiguous (two boxes checked in one group, or an answer that contradicts the checked option), would erase a real distinction, or needs structural changes.

   With a glossary, existing or newly chosen, put definitions there instead of in prose, and update it for every decided term specific to the project, following its existing format. In a new `GLOSSARY.md`, give each term in bold followed by one or two sentences saying what it is. Leave out implementation details and general programming concepts. Without a glossary, define terms where readers first meet them.

   Search the scope for each name you replaced: fix what you missed, and say in the summary which uses you left on purpose. Run the project's checks, then summarize what changed. If the project has a glossary that its agent instructions (such as `AGENTS.md` or `CLAUDE.md`) don't mention, suggest adding a line telling agents to use its terms and to flag conflicts with it.
