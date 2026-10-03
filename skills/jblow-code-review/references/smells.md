# Smell Catalog

Use this as the checklist during the review pass. Each entry: what to look for,
why Blow cares, and the shape of the fix. Remember the calibration rule: weight
by actual cost at this game's scale.

## Architecture & abstraction

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Engine-instead-of-game | `Engine/`, `Core/`, `Framework/` directories in a small game; abstraction layers over SDL/raylib/the platform layer that add nothing | Months of life spent on code that isn't the game | Delete the layer; call the library directly; let the two objects communicate |
| Speculative generality | Type parameters with one instantiation; config options never set; interfaces with one implementer; `IRenderable`, `AbstractWeaponFactory` | More code, worse names, imagined futures that arrive wrong | Write the specific version; generalize from the second real use case |
| Deep inheritance | Entity → Actor → Pawn → Character; virtual calls in hot loops; behavior spread across a hierarchy so no one file tells the truth | Can't read the code top-to-bottom; can't predict dispatch; cache-hostile | One fat entity struct + type enum + switch, or discriminated union; composition as plain fields |
| Framework-brain ECS | ECS library for a game with 300 entities; systems/components ceremony where a for-loop over an array would do | Indirection tax on every feature, paid forever | Arrays of structs, loops. Adopt ECS-ish layout only when a profiled hot loop demands it |
| Manager/Singleton/Factory ceremony | `XxxManager`, `ServiceLocator`, dependency injection containers in a game | Global state wearing a costume, plus indirection | A plain global, or pass the pointer. Be honest about globals |
| Event/observer spaghetti | Gameplay logic firing events handled elsewhere; message buses; signals connecting everything | Control flow becomes archaeology; ordering bugs; debugging requires telepathy | Direct function calls in visible order. Events only across genuine module boundaries (e.g., UI ↔ game) |
| Getter/setter boilerplate | `get_x()/set_x()` wrapping public-in-spirit fields; properties with hidden side effects | Ceremony; hidden control flow if setters do work | Public fields on plain structs |

## Code shape

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Function confetti | Five-line functions called once, chained; logic that reads as a scavenger hunt | Reader rebuilds the call graph mentally; state flow hidden in parameter plumbing | Inline single-callers; long straight-line functions with comment headers per section (see Carmack email) |
| Callback indirection | Lambdas/closures/function pointers where a direct call works; "flexible" hook systems | Same as events: invisible flow | Direct calls; a switch on an enum beats a table of callbacks you can't grep |
| Clever metaprogramming | Template/trait/macro machinery to save trivial repetition | Compile time, error messages, unreadability | Repeat yourself a little; compress only real, painful repetition |
| Wrong-layer error handling | Exceptions for game logic; error monads threaded through everything; or its evil twin: `try/catch(...) {}` and null-checks that convert impossible states into silent wrongness | Hidden control flow, or hidden bugs | Assert impossible states (crash in dev); explicit return values for genuinely expected failures (file not found) |
| Comment-free cleverness / dogmatic no-comments | "Self-documenting" code that isn't | Re-derivation cost for every reader including future-you | Comments that say *why*; block headers over extraction |

## Memory & performance (hot paths only — check scale first)

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Per-frame heap traffic | `new`/`malloc`/`List<T>` growth, string building, boxing, LINQ/closures (C#) inside update/render | GC spikes, allocator contention, frame hitches | Preallocate; arena/temporary allocator reset per frame; reuse buffers |
| Pointer-chasing hot loops | Arrays of pointers to heap objects iterated per frame; linked lists in simulation | Cache misses dominate; performance unreasonable-about | Contiguous arrays of structs; SoA if a profiled loop needs it |
| Hidden per-frame work | Property accessors doing searches; `FindObjectByName` in update; per-frame string comparison/hashing; per-frame file/registry/locale queries | Death by a thousand cuts, invisible at call sites | Resolve once at load; store the pointer/index/handle |
| Premature optimization | Object pools, SIMD, lockfree queues in a puzzle game with 200 actors | Life-time spent, complexity bought, nothing gained | Delete it. Profile first. Blow explicitly blesses "generates garbage, ships fine" at small scale |
| Allocation lifetime chaos | shared_ptr webs, ownership nobody can state, ref-count cycles | Both a perf and a comprehension tax | Clear single owners; handles/indices into arrays instead of shared pointers |

## Dependencies & build

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Dependency graph | Lockfiles with hundreds of transitive packages; a JSON lib + a math lib + a logging framework + an events lib for a 10k-line game | Un-debuggable stack; upgrades break you; collapse-of-civilization territory | Vendor small readable libs (stb-style); write the 100 lines yourself; know your whole stack |
| Build friction | Multi-minute builds; codegen steps; heavy template headers included everywhere; asset pipeline rebaking on every tweak | Every iteration taxed, forever; compounding damage to the design process | Fewer TUs/unity build, forward declarations, split hot-edit data from code, hot-reloadable assets |
| Engine fighting | Working against Unity/Unreal defaults with elaborate wrappers; abstracting the engine "in case we switch" | Double indirection: engine + your fake engine | Use the engine idiomatically, or don't use it. Never both |

## Gameplay & design-in-code

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Frame-rate-dependent gameplay | Movement without `dt`; physics on variable timestep; `dt`-scaled forces that diverge across frame rates | Game behaves differently per machine; determinism impossible | Fixed timestep for simulation, render interpolation; audit float accumulation |
| Nondeterminism | Wall-clock reads in logic, unordered-container iteration driving gameplay, unseeded/global RNG | No replays, no rewind, unreproducible bugs | Seeded RNG owned by the sim; ordered iteration; sim time, not real time |
| Magic-number tuning | Feel constants (jump force, coyote time, camera lerp) buried as literals deep in code | Every design tweak is a recompile; feel never gets iterated | Pull into one tweakable place; hot-reload or in-game editing if cheap |
| Latency mush | Input queued through layers of events/buffers before applying; smoothing on player input | The game feels bad and nobody knows why | Sample input late, apply in the same frame's sim step; smooth the camera, not the input |
| No debug affordances | No debug draw, no state dump, no way to spawn a test scenario, restart = replay 5 minutes | Iteration speed dies; design suffers silently | Debug overlay, instant scenario load, in-game tweak menu — worth real engineering |
| Content scaffolding | Weapon/enemy/dialogue "systems" supporting one weapon, one enemy, no dialogue | Speculative generality, design edition | Build the one mechanic deeply; systematize when the second one is real |

## Things to praise when found

Plain structs and arrays. A long, readable update function. A switch over an enum.
An arena allocator. Fixed timestep. Asserts. A debug overlay. Five dependencies
instead of fifty. Code where you can point at any line and say what the machine
does. A shipped scope. Say these out loud in the review — calibrated praise is
what makes the criticism credible.
