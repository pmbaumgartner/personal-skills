---
name: roborev-analyze-refactor
description: "Identify concrete refactoring opportunities for maintainability. Use for roborev refactor analysis."
---

# Roborev: Refactor

Read the files in the scope requested by the user before applying the instructions below. Report findings; do not modify code unless the user asks for changes.

Source: [refactor.txt](https://github.com/kenn-io/roborev/blob/0cc4d482018fb022341adbdd84ff1e6c23a14083/internal/prompt/analyze/refactor.txt). The upstream prompt below is preserved verbatim.

## Instructions

Analyze the provided code for refactoring opportunities that would improve readability, maintainability, and code quality.

Your task:
1. Identify code smells and anti-patterns:
   - Long functions that should be broken up
   - Complex conditionals that could be simplified
   - Poor naming that obscures intent
   - Tight coupling that limits flexibility
   - Missing abstractions or over-abstraction
2. Propose specific refactorings with clear rationale
3. Prioritize by impact and safety

Output format:
- **CODE SMELLS:** List issues with locations and severity
- **REFACTORING SUGGESTIONS:** Specific changes with before/after examples
- **PRIORITY ORDER:** Ranked list of which changes to make first
- **DEPENDENCIES:** Note if any refactorings should be done together
