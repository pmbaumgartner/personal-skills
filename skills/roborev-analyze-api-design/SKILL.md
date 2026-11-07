---
name: roborev-analyze-api-design
description: "Review public API consistency, naming, signatures, and usability. Use for roborev api-design analysis."
---

# Roborev: Api Design

Read the files in the scope requested by the user before applying the instructions below. Report findings; do not modify code unless the user asks for changes.

Source: [api_design.txt](https://github.com/kenn-io/roborev/blob/0cc4d482018fb022341adbdd84ff1e6c23a14083/internal/prompt/analyze/api_design.txt). The upstream prompt below is preserved verbatim.

## Instructions

Analyze the provided code for API design consistency and best practices.

Your task:
1. Review the public API surface:
   - Function/method signatures
   - Type definitions and interfaces
   - Exported constants and variables
   - Error handling patterns
2. Check for consistency issues:
   - Naming conventions
   - Parameter ordering
   - Return value patterns
   - Error types and messages
3. Identify usability concerns:
   - Confusing or ambiguous APIs
   - Missing convenience methods
   - Awkward usage patterns

Output format:
- **CONSISTENCY ISSUES:** Inconsistent patterns across the API
- **USABILITY CONCERNS:** APIs that are hard to use correctly
- **NAMING SUGGESTIONS:** Specific renames for clarity
- **DESIGN IMPROVEMENTS:** Structural changes to improve the API
