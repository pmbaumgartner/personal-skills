# Smell Catalog

Checklist for the review pass: what to look for, what it costs, and the shape of
the fix. Weight by actual cost at this game's scale, and verify usage claims
before flagging.

## Architecture & abstraction

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Engine-instead-of-game | `Engine/`, `Core/`, `Framework/` directories in a small game; layers over SDL, raylib, or the platform that add nothing | Months spent on code that isn't the game | Delete the layer; call the library directly |
| Speculative generality | Type parameters with one instantiation; options never set; interfaces with one implementer | More code, worse names, imagined futures that arrive wrong | Write the specific version; compress once a second real use exists |
| Deep inheritance | Entity → Actor → Pawn → Character; behavior spread so no one file tells the truth; virtual calls in hot loops | Can't read top-to-bottom; can't predict dispatch; cache-hostile | Shallow structure: a type field and a switch, a discriminated union, or composition as plain fields |
| Framework-brain ECS | ECS library for a few hundred entities; systems and components where a loop over an array would do | Indirection tax on every feature, forever | Arrays of structs and loops; ECS-like layout only where a profiled loop demands it |
| Manager/Singleton/Factory ceremony | `XxxManager`, service locators, DI containers | Global state in a costume, plus indirection | A plain global, or pass the pointer |
| Event/observer spaghetti | Gameplay logic fired as events handled elsewhere; message buses; signals everywhere | Control flow becomes archaeology; ordering bugs | Direct calls in visible order; events only across real module boundaries such as UI and game |
| Getter/setter boilerplate | Accessors wrapping plain fields; properties with side effects | Ceremony, or hidden control flow | Public fields on plain structs |
| Hostile API shape | Callers must build large object graphs before the first call; no way to take control of one piece without abandoning the API; caller data mirrored into retained objects kept in sync | Integration discontinuities: integration work and sync bugs dwarf the work the API saves | Judge from calling code; offer finer-grained entry points; offer immediate-mode calls so callers own their data |

## Code shape

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Function confetti | Five-line functions called once, chained into a scavenger hunt | Reader rebuilds the call graph; state flow hidden in parameter plumbing | Inline single-use code; long straight-line functions with comment headers |
| Long functions mutating shared state | Inline code that reads and writes globals or many unrelated fields | Order-dependent bugs; hard to test or reason about | Keep it long, but pass inputs and return outputs where practical |
| Fancy data structure by default | Hash maps, trees, or custom containers for tiny or rarely searched collections | Code, bugs, and indirection for no measured gain | A flat array; upgrade when profiling says so |
| Callback indirection | Closures and function pointers where a direct call works; "flexible" hook systems | Invisible flow; can't grep for callers | Direct calls; a switch over an enum |
| Clever metaprogramming | Templates, traits, or macros saving trivial repetition | Compile time, error messages, unreadability | Repeat a little; compress only real, painful repetition |
| Wrong-layer error handling | Exceptions for game logic; error plumbing through everything; or `catch {}` and null checks that turn impossible states into silent wrongness | Hidden control flow, or hidden bugs | Assert impossible states; explicit returns for expected failures such as a missing file |
| Rare conditional paths | Work skipped on most frames and done only on some trigger | Rarely exercised code hides bugs and causes frame spikes | Do the work every frame when the cost allows |
| Comment-free cleverness | "Self-documenting" code that isn't | Every reader re-derives intent | Comments that say why; headers over extraction |

## Runtime cost

Needless work is a defect at any scale. Effortful optimization is not.

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Hidden per-frame work | Accessors doing searches; lookups by name in update; per-frame string building, hashing, or file queries | Death by a thousand cuts, invisible at call sites | Resolve once at load; store the index or handle |
| Per-frame heap traffic (hot paths) | Allocation, list growth, boxing, LINQ or closures (C#) in update or render | GC spikes, frame hitches | Preallocate; arena or per-frame temporary allocator; reuse buffers |
| Pointer-chasing hot loops | Arrays of pointers to heap objects iterated per frame; linked lists in simulation | Cache misses dominate | Contiguous arrays; split hot fields if a profiled loop needs it |
| Virtual dispatch in hot loops | Polymorphic calls per element per frame | Measurable slowdown versus a switch on plain data | Switch over a type field, or group elements by type |
| Premature optimization | Pools, SIMD, lock-free queues in a game with a few hundred actors | Complexity bought, nothing gained | Delete it; profile first |
| Ownership chaos | `shared_ptr` webs, unclear owners, reference cycles | Performance and comprehension tax | Single clear owners; indices or handles into arrays |

## Dependencies & build

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Dependency graph | Hundreds of transitive packages; separate JSON, math, logging, and event libraries for a small game | Undebuggable stack; upgrades break you | Vendor small readable libraries (stb-style); write the 100 lines yourself |
| Build friction | Multi-minute builds; codegen steps; heavy headers everywhere; asset pipelines rebaking on every tweak | Every iteration taxed, forever | Unity builds, fewer includes, hot-reloadable data separated from code |
| Engine fighting | Elaborate wrappers against engine defaults; abstracting the engine "in case we switch" | Engine plus your fake engine | Use the engine idiomatically, or don't use it |
| Silenced checks | Warnings disabled or ignored; analyzers absent or suppressed wholesale | Known bug classes ship | Warnings on and clean; run available static analyzers |

## Gameplay & design in code

| Smell | Look for | The cost | The fix |
|---|---|---|---|
| Frame-rate-dependent gameplay | Movement without `dt`; physics on a variable timestep | Different behavior per machine | Fixed simulation timestep with render interpolation |
| Nondeterminism | Wall-clock reads in logic; unordered iteration driving gameplay; unseeded global RNG | Unreproducible bugs; no replays | Seeded RNG owned by the simulation; ordered iteration; simulation time |
| Buried tuning | Feel constants deep in code as literals | Every tweak is a recompile; feel never gets iterated | One tweakable place; hot reload or in-game editing if cheap |
| Latency added by layers | Input passed through queues, events, or smoothing before it applies | The game feels mushy | Sample late, apply in the same frame; smooth the camera, not the input |
| No debug affordances | No debug draw, state dump, scenario loading, or instant restart | Iteration dies; design suffers silently | Debug overlay, test-scenario load, tweak menu |
| Content scaffolding | Weapon, enemy, or dialogue "systems" serving one weapon, one enemy, no dialogue | Speculative generality, design edition | Build the one mechanic deeply; systematize when the second is real |

## Things to praise when found

Plain structs and arrays. A long, readable update function. A switch over an
enum. An arena allocator. A fixed timestep. Asserts. Clean warnings. A debug
overlay. Five dependencies instead of fifty. Code where any line's machine cost
is obvious. A shipped scope.
