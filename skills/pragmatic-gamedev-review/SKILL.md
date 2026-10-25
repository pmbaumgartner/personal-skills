---
name: pragmatic-gamedev-review
description: Review game and engine code through the pragmatic lens of Jonathan Blow, Casey Muratori, and John Carmack, focusing on overengineering, dependencies, needless runtime cost, iteration speed, debuggability, and shipping rather than conventional clean-code rules.
disable-model-invocation: true
---

# Pragmatic Gamedev Review

Review code with one question: **does this help ship a good game with the time
and frames available, or is it friction?**

This lens comes from Jonathan Blow, Casey Muratori, and John Carmack. It often
*inverts* conventional clean-code virtues (small functions, DRY, patterns,
interfaces, layers). Read `references/principles.md` before the first review; it
holds each person's positions with sources. Use `references/smells.md` as the
checklist during the review pass.

## Shared core

- **Life-time cost.** Every abstraction, layer, option, and dependency costs
  writing, debugging, and permanent comprehension time. Specific code beats
  general code; generalize from real repetition, not imagined futures.
- **Frame-time cost.** Never do needless work, anywhere. Effortful optimization
  belongs only where a hot path is shown to need it.
- **Iteration speed.** Compile, load, and time-to-test-a-change are first-class
  concerns. Games are found by iterating.
- **Debuggability.** You must be able to read, step through, and fix everything
  the program depends on. Impossible states assert loudly instead of being
  handled quietly.

## Where they pull differently

Resolve these tensions explicitly instead of picking a slogan:

- **Inline vs. compress.** Blow and Carmack: leave single-use code inline; long
  straight-line functions are fine. Muratori: extract once repetition actually
  exists. Extraction is earned by a real second use, never by length alone.
- **Don't optimize vs. don't pessimize.** Blow's "don't optimize" targets clever
  effort in cold code. Muratori's non-pessimization says code should still not
  waste the machine. Flag needless work everywhere; flag missing optimization
  only on a demonstrated hot path.
- **Visible mutation vs. pure functions.** Carmack likes inlined code *and*
  functions that take inputs and return outputs. Long functions are fine;
  long functions reaching into shared or global state are not.
- **Fewer tools vs. more checking.** Blow distrusts layers; Carmack runs every
  static analyzer he can. Tools that find bugs without becoming a runtime or
  build dependency are welcome. Layers the program must run through are debt.

## Review workflow

1. **Survey before judging.** Learn the game's scale, the per-frame path
   (update, physics, render, particles), the cold paths (init, menus, save/load,
   tooling), the layers between gameplay and the machine, and the dependency and
   build surface. Scale decides which performance findings matter.
2. **Verify before flagging.** Search the codebase to confirm "called from one
   place," "one implementer," "option never set," "unused," and "runs per
   frame" before claiming them. State build or load-time estimates as
   estimates.
3. **Review against the principles.** Weight findings by real cost. A ten-layer
   input abstraction outranks an unused variable. Cite whose principle a
   finding relies on when it sharpens the argument.
4. **Credit what is right.** Plain structs and arrays, readable update loops,
   switches over type fields, asserts, debug draw, hot reload, fixed timesteps,
   few dependencies. Calibrated praise makes criticism credible.
5. **Review design-facing code** for games: tuning values buried where a
   designer cannot iterate, systems built for content that does not exist,
   frame-rate-dependent gameplay, and input latency added by layering.

## Output format

Blunt, plain, and reasoned. Every criticism names its cost in time, bugs, or
frames. No hedging, no sandwiching, no persona. Do not present paraphrases as
quotes.

```
# Code Review: [project/file]

## The one thing that matters
[2-4 sentences: the biggest way this code costs the author time or frames.]

## What you did right
[Short, specific list. If nothing, say so and why.]

## Findings
[Ordered by cost, worst first. For each:]
### [Blunt title, e.g. "You wrote an engine instead of a game"]
- **What**: file/line refs, short excerpt
- **Cost**: life-time, frame-time, iteration, or bug surface
- **Instead**: the concrete, simpler alternative; code where it helps

## Design notes
[Games only: tuning, iteration, timing, latency, scaffolding.]

## Verdict
[One paragraph: will this ship, and what single change most improves
time-to-ship?]
```

Rewrites must honor the lens: plain data, straight-line flow, no new
abstractions, usually fewer lines than the original. Recommending a new pattern,
layer, or dependency requires a stated, overwhelming justification.

## Calibration

- **Don't sound gruff while giving conventional advice.** A review that
  recommends extracting interfaces and adding unit-test scaffolding for gameplay
  code has failed. Check recommendations against `references/principles.md`.
- **Scale performance judgments.** No pooling crusades in a 200-entity puzzle
  game; no shrugging at per-frame allocation in a bullet hell.
- **Respect working code.** Ugly, done, and cheap to keep is often a
  compliment. Separate mess that costs nothing from complexity that compounds.
- **Match the language.** In C, C++, Jai, Odin, Rust, or Zig, discuss layout and
  allocators directly. In C#/Unity, focus on GC pressure in hot paths and
  fighting the engine. In GC'd scripting languages, focus on structure and
  dependency weight.
- For non-game code, keep the lens but drop frame-budget and design sections.
