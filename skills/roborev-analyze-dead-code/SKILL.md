---
name: roborev-analyze-dead-code
description: "Find unused exports, unreachable paths, and stale code. Use for roborev dead-code analysis."
---

# Roborev: Dead Code

Read the files in the scope requested by the user before applying the instructions below. Report findings; do not modify code unless the user asks for changes.

Source: [dead_code.txt](https://github.com/kenn-io/roborev/blob/0cc4d482018fb022341adbdd84ff1e6c23a14083/internal/prompt/analyze/dead_code.txt). The upstream prompt below is preserved verbatim.

## Instructions

Analyze the provided code for dead code, unused exports, and unreachable code paths.

Your task:
1. Identify potentially dead code:
   - Unused exported functions, types, or variables
   - Unreachable code after return/panic/os.Exit
   - Commented-out code that should be removed
   - Debug/test code left in production
2. Check for unused imports and dependencies
3. Find code that exists but appears to never be called

Output format:
- **UNUSED EXPORTS:** Exported symbols that appear to have no callers
- **UNREACHABLE CODE:** Code paths that can never execute
- **STALE CODE:** Old code that should likely be removed
- **CONFIDENCE LEVEL:** High/Medium/Low for each finding (some may have external callers)

Note: Some exports may be used by external packages or via reflection. Flag these as lower confidence.
