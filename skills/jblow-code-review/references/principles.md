# Blow's Principles, With Sources

Read this before performing a review. These are paraphrases of positions Jonathan
Blow has stated publicly, with where they come from. Never present paraphrases as
verbatim quotes.

## From "How to Program Independent Games" (UC Berkeley CSUA talk, 2011)

This talk is the spine of the philosophy. Its thesis: as a programmer your
instinct is to "optimize" — but you optimize the wrong function. The thing to
optimize is *how much of your life a finished game costs*.

1. **The hardest skill is deciding what not to do.** Most "improvements" (a
   resource manager, a general event system, a scripting layer, an editor) are
   things you'll never need. Every one costs implementation time, debugging time,
   and permanent comprehension overhead.

2. **Specific over general.** Write the code that solves the problem in front of
   you. The general version: takes longer to write, has more edge cases, is harder
   to name, is harder to debug, and usually predicts the wrong future. When the
   second use case actually arrives, generalize *then*, from two real examples
   instead of one imagined one. (This aligns with Casey Muratori's "compression-
   oriented programming": write it straight, compress repetition after it exists.)

3. **Straight-line code.** If a block is called from one place, consider leaving
   it inline. Extracting it to a function means the reader must jump, must trust
   the name, must reconstruct the data flow through parameters. Blow hosts John
   Carmack's famous email on inlined code (number-none.com/blow/
   john_carmack_on_inlined_code.htm), which argues large inline functions make
   execution order and state mutation visible, and prevent functions from growing
   surprise callers. Long functions that read top-to-bottom are fine. Good.

4. **Don't optimize prematurely — including "code quality" optimization.**
   Pooling objects in a game that allocates trivially, caching things that are
   computed once, "fixing" O(n²) over n=30. Profile-visible costs only. The same
   discipline applies to refactoring: refactor when the mess actually bites.

5. **It's okay if it's a little bad, as long as it ships.** A finished game with
   messy corners beats an immaculate half-engine. Most code in a shipped game is
   written once and barely revisited.

6. **Data should just be data.** Plain structs, arrays, obvious ownership.
   Getters/setters wrapping trivial fields, deep encapsulation of things that are
   just values, "manager" classes managing one thing — ceremony with no payoff.

## From the Jai talks / "A Programming Language for Games" series (2014–)

7. **Friction is the enemy; the compiler is part of the game loop.** Jai exists
   because C++ compile times and complexity tax every single iteration. In a
   review: anything that slows edit-compile-run — heavy template use, header
   sprawl, unity-build-hostile structure, asset pipelines that rebake the world
   for one tweak — is a first-class defect, not a nitpick.

8. **The machine is not an abstract platform.** Memory is real, caches are real.
   Prefer Structure-of-Arrays or contiguous AoS where iteration is hot; avoid
   pointer-chasing graphs of heap-allocated objects in per-frame loops. Prefer
   arena/temporary allocators (Jai has a built-in temporary allocator reset per
   frame) over ad-hoc new/delete or per-frame GC garbage.

9. **RAII/exceptions/hidden control flow are distrusted.** Destructors,
   exceptions, operator overloading, property accessors with side effects — code
   that runs without being visible at the call site makes programs hard to reason
   about. Prefer explicit init/deinit, explicit error returns, visible flow.

10. **Big Agenda OOP is rejected.** Inheritance hierarchies for game entities
    (Entity → Actor → Pawn → Character...), virtual dispatch as the default,
    patterns (Factory, Singleton, Visitor, Observer) applied as vocabulary rather
    than necessity. Blow's entities are typically a single fat struct (a
    "megastruct") with a type enum and a switch, or discriminated unions. He is
    *also* skeptical of dogmatic ECS frameworks — ECS-as-religion is just another
    Big Agenda. The test is always: does this structure make the game simpler to
    write and change, or does it make the framework happy?

## From "Preventing the Collapse of Civilization" (DevGAMM 2019)

11. **Software gets worse when nobody understands the full stack.** Layers
    accumulate; capability is lost; everything is slower than it was on machines
    a thousand times weaker. In a review: dependencies are not free. Flag every
    library that could be replaced with a page of your own code, every framework
    feature used because it exists rather than because it's needed. Robustness
    comes from simplicity — fewer parts, fewer failure modes, one person able to
    hold the whole thing in their head.

12. **You should be able to debug anything in your program.** If a bug lands in
    a dependency you can't read, can't build, or can't step through, you've lost.
    Prefer vendored, readable, small libraries (stb-style single headers) over
    package-manager graphs of transitive dependencies.

## On correctness and bugs (talks, streams, Q&As)

13. **Assert aggressively; crash in development.** An impossible state should
    stop the program at the moment of the crime, not be null-checked into
    silently wrong behavior three systems later. Defensive programming that
    "handles" states that cannot legitimately occur is bug-hiding.

14. **Determinism is a feature.** Braid's rewind and The Witness's engine rely
    on simulation you can replay. Fixed timesteps for gameplay logic, no
    dependence on frame rate, no gameplay reads of wall-clock time, care with
    float accumulation and iteration-order-dependent logic.

## On comments and naming

15. **Blow is not a "self-documenting code" purist.** He pushes back on the
    Clean Code position that comments are failures. A comment explaining *why*,
    or a header note saying what a chunk does, beats splitting code into a
    confetti of named five-line functions. Flag comment-free cleverness and
    flag comment-as-function-extraction equally.

## On game design in code

16. **Games are found through iteration.** The value of the codebase is measured
    in how fast you can try a design idea. Hot reload, in-game parameter tweaking,
    debug draw, instant restart to a test state — these are worth real
    engineering. A "well-architected" game you can only test by playing five
    minutes from the main menu is badly architected.

17. **Depth over breadth; don't build for content that doesn't exist.** Systems
    generalized for enemy types, weapons, or mechanics that are not designed yet
    are speculation, same as code generality. Build the mechanic, find the depth,
    then extend.

18. **Feel lives in the details.** Input latency (sample late, apply same frame),
    camera code, easing/tuning constants exposed for tweaking, animation blending
    that doesn't fight responsiveness. These deserve review attention that
    "architecture" usually steals.
