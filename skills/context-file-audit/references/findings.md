# Evidence

Read this when the user asks why a recommendation holds. All are arXiv preprints from
2025-2026. Most use Python repos and one sample per task, and effects vary by model.

- **Context files barely move task success but change behavior and cost.**
  - Gloaguen et al., "Evaluating AGENTS.md" (arXiv:2602.11988 v3), four agents: neither
    generated nor developer-written files significantly changed success, and both raised cost
    by about 20%. Agents used whatever tools the file mentioned. Overviews didn't help them
    find files, and removing testing instructions cut cost with no accuracy loss. Generated
    files helped only once the repo's other docs were deleted.
  - Khatri (arXiv:2607.27250): no detectable effect for Claude Code or Codex. A slow-test
    warning cut full-suite runs.
  - Lulla et al. (arXiv:2601.20404): existing AGENTS.md files shortened runtime, though
    correctness wasn't checked.
- **Structure doesn't change adherence; session length and wording do.**
  - McMillan (arXiv:2605.10039): file size, instruction position, multi-file layout, and
    conflicting files had no effect. Compliance faded as the session went on.
  - Tsuchida et al. (arXiv:2611.04367): conditional and "never X without Y" wordings were
    followed least, by model-dependent margins.
- **Stale files override the code.** Xu & Wu (arXiv:2610.30571): agents followed an outdated
  file over the existing code most of the time, sometimes rewriting working code to match.
- **Scope-limiting "don't" rules help; generic directives don't.**
  - Zhang et al. (arXiv:2604.11088): the helpful rules were negative constraints, the harmful
    ones generic positive directives. The statistics are weak and only one model was tested.
  - Yang & Ding (arXiv:2608.23067): anti-pattern rules helped within skills.
- **Enforcement beats prose.** Sharma, ContextCov (arXiv:2603.00822): turning instructions
  into executable checks raised both compliance and resolve rate.
- **Skills help only when curated and focused.**
  - SkillsBench (arXiv:2602.12670): curated, focused skills helped. Self-generated ones hurt.
  - SWE-Skills-Bench (arXiv:2603.15401 v2): most public SWE skills had no effect, and
    template-heavy ones misled agents.
  - Yang & Ding (arXiv:2608.23067): always-loaded skills lowered pass rates and raised cost.
- **Vendor guidance** (Claude Code, Codex, Cursor, Copilot, and Gemini CLI docs, checked Nov
  2026): keep files short and limited to what isn't discoverable. Move part-of-codebase rules
  and procedures to path-scoped rules and skills. Use hooks or deny rules for rules with no
  exceptions. Drop emphasis and other workarounds for older models. Loading rules change
  often, so re-check the docs before relying on one.
