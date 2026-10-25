# Principles, With Sources

Paraphrases of publicly stated positions unless shown in quotation marks. Never
present a paraphrase as a quote, and do not attribute a position to someone who
did not take it.

## Jonathan Blow

**"How to Program Independent Games"** (talk to the UC Berkeley Computer
Science Undergraduate Association, April 1, 2011; slides and audio on
the-witness.net). The thesis: programmers optimize the wrong function. The
target is how much of your life a finished game costs.

1. **Deciding what not to do is the hardest skill.** Resource managers, general
   event systems, scripting layers, and editors are usually unneeded, and each
   costs implementation, debugging, and permanent comprehension time.
2. **Specific over general.** A generalized system is usually worse than a
   specific one: it takes longer, has more edge cases, is harder to name and
   debug, and predicts the wrong future. Replying to a commenter defending
   decoupled designs, he wrote: "Why don't you just, you know, let the two
   objects communicate?"
3. **Data structures are optimizations.** The talk's example is a linear search
   over an array instead of a hash table. Blow later said the specific choice
   matters little; the point is not to pay for an optimization, and the
   assumptions it bakes in, before you need it.
4. **Don't optimize prematurely.** Optimization constrains later changes; wait
   until a cost is visible. The same applies to "quality" refactoring.
5. **Straight-line code.** Single-use logic stays inline rather than being
   split into small functions that are harder to follow and step through.

**The Jai talks** (beginning with "Ideas about a new programming language for
games", September 2014, and "A Programming Language for Games, talk #2").

6. **Friction is the enemy.** Compile times and language complexity tax every
   iteration; slow edit-compile-run is a real defect.
7. **Hidden control flow is distrusted.** He questioned the value of RAII, and
   Jai has no exceptions. Prefer explicit init and cleanup (Jai uses `defer`)
   and explicit error returns. This is not a rejection of operator overloading,
   which Jai supports for math types.

**"Preventing the Collapse of Civilization"** (DevGAMM Moscow, May 2019).

8. **Layers erode capability.** Fewer and fewer people understand how software
   works underneath while dependence on it grows, and much apparent progress is
   free-riding on hardware. Dependencies are not free; robustness comes from
   fewer parts one person can hold in their head.
9. **Software is in decline, not just unoptimized.** This is the counterweight
   to "don't optimize": needless slowness and fragility are not acceptable just
   because nobody profiled them.

**Broader positions** (streams and Q&As; no single canonical source, so cite
these only as general positions).

10. **Assert aggressively; crash in development.** Stop at the moment an
    impossible state appears instead of null-checking into silent wrongness.
11. **Skeptical of object-oriented dogma.** Deep inheritance hierarchies and
    design patterns used as vocabulary serve the framework rather than the
    game. Shallow, plain structure is fine.
12. **Don't build for content that doesn't exist.** Systems generalized for
    undesigned enemies, weapons, or mechanics are speculative generality on
    the design side.

## Casey Muratori

**"Semantic Compression"** (caseymuratori.com, May 28, 2014, in his series of
posts written while working on The Witness).

1. **Write it specifically, then compress.** Write exactly what each case
   needs and get it working. Pull out shared code only once the pattern appears
   a second time, so there are two real examples to design against. "Make your
   code usable before you try to make it reusable."
2. **Objects emerge later.** Don't design class hierarchies up front; structure
   arises from compressing procedural code.

**"Designing and Evaluating Reusable Components"** (talk, 2004, from his work
on Granny at RAD Game Tools).

3. **"Always write the usage code first."** Judge an API, including a
   third-party one, by sketching the code that would call it before reading
   headers or documentation.
4. **Avoid integration discontinuities.** The main pitfall of an API is a
   sudden jump in integration work when a requirement goes slightly beyond what
   it handles, usually near ship. Granularity trades flexibility for
   simplicity; a good API lets callers move to finer control in small steps.
5. **Don't force retention.** An API that keeps copies of caller-owned data
   forces mirroring and synchronization. Every retained-mode call should have
   an immediate-mode equivalent.

**"Refterm Lecture Part 1 – Philosophies of Optimization"** (Molly Rocket on
YouTube, October 2021).

6. **Optimization, non-pessimization, fake optimization.** Real optimization is
   measured, targeted, and costly. Non-pessimization means not doing needless
   work in the first place, and applies everywhere. Fake optimization is
   repeating tips from unrelated cases without measuring. Refterm's large
   speedup over Windows Terminal came mostly from non-pessimization.

**"'Clean' Code, Horrible Performance"** (Computer Enhance, February 2023).

7. **Clean-code rules have a measurable cost.** Applying the structural rules
   drawn from *Clean Code* (polymorphism over switches, tiny functions) to a
   shape-area example made the hot loop many times slower than a switch over a
   type field on plain data. In hot code, prefer the switch.

**"The Thirty-Million-Line Problem"** (talk, 2015).

8. **The stack is too deep.** Like Blow's collapse talk: massive layers between
   program and hardware are a cost, not a given.

## John Carmack

**Email on inlined code** (March 13, 2007; republished in 2014 on Blow's site,
number-none.com, with a new preface by Carmack).

1. **"If a function is only called from a single place, consider inlining
   it."** Inline code shows execution order and state mutation, and keeps
   functions from being called elsewhere in unexpected states.
2. **Do the work every frame.** It is often better to perform an operation and
   then ignore some of the results than to skip it conditionally. That costs
   more absolute time but reduces frame-time variability and avoids skipped
   state updates that other code depends on.
3. **The 2014 preface reframes it.** The real enemy addressed by inlining is
   unexpected dependency and mutation of state, which functional programming
   solves more directly. Many state changes are best kept inline; when inline
   code gets unwieldy, factor blocks into pure functions.

**"Functional Programming in C++"** (#AltDevBlogADay, April 2012).

4. **Minimize state, pragmatically.** A pure function only looks at its
   parameters and does not read or update global state, so it is easier to
   test, reuse, reason about, and run on other threads. Making a function
   mostly pure gets most of the benefit; there is no need to leave C++.

**"Static Code Analysis"** (#AltDevBlogADay, December 2011; also his QuakeCon
2011 keynote).

5. **Aggressively pursue static analysis.** In a large enough codebase, any
   class of error that is syntactically legal probably exists. id compiled at
   warning level 4 with warnings as errors and ran multiple analyzers.

**"Latency Mitigation Strategies"** (#AltDevBlogADay, February 2013).

6. **Sample late, don't buffer.** Sample input just before it is needed rather
   than at the start of the frame, and avoid work queues and GPU buffering on
   the responsiveness path, since each can add a frame of latency.

**"Parallel Implementations"** (#AltDevBlogADay, November 2011).

7. **Replace risky systems side by side.** Keep the old implementation working
   and switchable beside the new one so they can be compared, then drop the
   loser. Pure functions are the easiest to swap. "Code fearlessly on the copy,
   while the original remains fully functional and unmolested."

**Lex Fridman Podcast #309** (August 2022).

8. **Use a debugger.** Run new code under a debugger to see what it actually
   does; your head is a faulty interpreter.
