---
name: roborev-analyze-complexity
description: "Find complexity hotspots and suggest simplifications. Use for roborev complexity analysis."
---

# Roborev: Complexity

Read the files in the scope requested by the user before applying the instructions below. Report findings; do not modify code unless the user asks for changes.

Source: [complexity.txt](https://github.com/kenn-io/roborev/blob/0cc4d482018fb022341adbdd84ff1e6c23a14083/internal/prompt/analyze/complexity.txt). The upstream prompt below is preserved verbatim.

## Instructions

Analyze the provided code for complexity issues and suggest simplifications.

Your task:
1. Identify complexity hotspots:
   - Functions with high cyclomatic complexity
   - Deeply nested control flow
   - Complex boolean expressions
   - Functions with too many parameters
   - Large switch statements or if-else chains
2. Assess cognitive load for each complex area
3. Suggest specific simplifications

Output format:
- **COMPLEXITY HOTSPOTS:** List functions/areas with complexity indicators
- **COGNITIVE LOAD ISSUES:** Parts that are hard to understand at a glance
- **SIMPLIFICATION SUGGESTIONS:** Concrete ways to reduce complexity
- **TRADE-OFFS:** Any trade-offs to consider (performance, flexibility, etc.)
